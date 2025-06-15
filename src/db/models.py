import sys
import os
from typing import Optional, List, Dict, Any, Union

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError as e:
    print(f"[-] Error importing mysql.connector: {e}")
    print("[*] Install with: pip install mysql-connector-python")
    sys.exit(1)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import get_db_config
except ImportError:
    utils_dir = os.path.join(os.path.dirname(current_dir), 'utils')
    sys.path.insert(0, utils_dir)
    try:
        from config import get_db_config
    except ImportError:
        print("[-] Error: Cannot find config module")
        sys.exit(1)

try:
    from encrypt import decrypt
except ImportError:
    print("[-] Warning: encrypt.py not found, encryption features disabled")
    encrypt = None
    decrypt = None

class _DatabaseConnection:
    def __init__(self) -> None:
        try:
            config = get_db_config()
            self.params: Dict[str, Any] = config.get_connection_params()
        except Exception as e:
            print(f"[-] Error loading database config: {e}")
            raise
        
        self.connection: Optional[mysql.connector.MySQLConnection] = None
    
    def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(**self.params)
            if self.connection and self.connection.is_connected():
                print(f"[+] Connected to database: {self.params['database']}")
                return True
            return False
        except Error as e:
            print(f"[-] Database connection failed: {e}")
            return False
        except Exception as e:
            print(f"[-] Unexpected connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("[-] Database connection closed")
        except Exception as e:
            print(f"[-] Error closing connection: {e}")
    
    def execute_query(self, query: str, params: Optional[Union[tuple, Dict[str, Any]]] = None) -> Optional[Union[List[Dict[str, Any]], int]]:
        try:
            if not self.connection:
                print("[-] No database connection")
                return None
                
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                result = cursor.lastrowid
                cursor.close()
                return result
        except Error as e:
            print(f"[-] Query execution failed: {e}")
            return None
        except Exception as e:
            print(f"[-] Unexpected query error: {e}")
            return None

class _AutoDecryptHelper:
    def __init__(self, db_connection: _DatabaseConnection) -> None:
        self.db = db_connection
        self.encryption_key: Optional[bytes] = None
        
        try:
            config = get_db_config()
            encryption_password = getattr(config, 'get_encryption_password', lambda: None)()
            if encryption_password and decrypt is not None:
                self.set_encryption_key(encryption_password)
                print(f"[+] Decryption key loaded from configuration")
            else:
                print("[*] No encryption password found in configuration, using default key")
                self.set_encryption_key("default_key_123")
        except Exception as e:
            print(f"[-] Error loading encryption key from config: {e}")
            self.set_encryption_key("default_key_123")
    
    def set_encryption_key(self, key_string: str) -> bool:
        try:
            if decrypt is None:
                print("[-] Encryption module not available")
                return False
            
            key_bytes = key_string.encode('utf-8')
            if len(key_bytes) < 16:
                key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
            elif len(key_bytes) > 16:
                key_bytes = key_bytes[:16]
            
            self.encryption_key = key_bytes
            return True
        except Exception as e:
            print(f"[-] Error setting encryption key: {e}")
            return False
    
    def is_data_encrypted(self, text: str) -> bool:
        """Check if data appears to be encrypted (hexadecimal format)"""
        try:
            if not text or len(text) < 16:
                return False
            if len(text) % 32 != 0:
                return False
            bytes.fromhex(text)
            return True
        except (ValueError, TypeError):
            return False
    
    def smart_decrypt(self, text: str) -> str:
        try:
            if not text:
                return text
            
            if not self.is_data_encrypted(text):
                return text
            
            if self.encryption_key is None or decrypt is None:
                return text
            
            encrypted_bytes = bytes.fromhex(text)
            decrypted_bytes = decrypt(self.encryption_key, encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return text
    
    def process_profile_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        if not profile:
            return profile
        
        return {
            'applicant_id': profile['applicant_id'],
            'first_name': self.smart_decrypt(str(profile['first_name'])) if profile['first_name'] else '',
            'last_name': self.smart_decrypt(str(profile['last_name'])) if profile['last_name'] else '',
            'date_of_birth': self.smart_decrypt(str(profile['date_of_birth'])) if profile['date_of_birth'] else '',
            'address': self.smart_decrypt(str(profile['address'])) if profile['address'] else '',
            'phone_number': self.smart_decrypt(str(profile['phone_number'])) if profile['phone_number'] else ''
        }

class _ApplicantProfile:
    def __init__(self, db_connection: _DatabaseConnection) -> None:
        self.db = db_connection
    
    def insert(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%(first_name)s, %(last_name)s, %(date_of_birth)s, %(address)s, %(phone_number)s)
        """
        return self.db.execute_query(query, data)
    
    def get_by_id(self, applicant_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM ApplicantProfile WHERE applicant_id = %s"
        result = self.db.execute_query(query, (applicant_id,))
        return result[0] if result else None
    
    def get_all(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM ApplicantProfile ORDER BY applicant_id DESC"
        result = self.db.execute_query(query)
        return result if result else []
    
    def update(self, applicant_id: int, data: Dict[str, Any]) -> Optional[int]:
        try:
            fields = ", ".join([f"{key} = %({key})s" for key in data.keys()])
            query = f"UPDATE ApplicantProfile SET {fields} WHERE applicant_id = %(applicant_id)s"
            data['applicant_id'] = applicant_id
            return self.db.execute_query(query, data)
        except Exception as e:
            print(f"[-] Error updating applicant: {e}")
            return None
    
    def delete(self, applicant_id: int) -> Optional[int]:
        query = "DELETE FROM ApplicantProfile WHERE applicant_id = %s"
        return self.db.execute_query(query, (applicant_id,))

class _ApplicationDetail:
    def __init__(self, db_connection: _DatabaseConnection) -> None:
        self.db = db_connection
    
    def insert(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
        VALUES (%(applicant_id)s, %(application_role)s, %(cv_path)s)
        """
        return self.db.execute_query(query, data)
    
    def get_all_with_profiles(self) -> List[Dict[str, Any]]:
        query = """
        SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
        FROM ApplicationDetail ad 
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
        ORDER BY ad.detail_id DESC
        """
        result = self.db.execute_query(query)
        return result if result else []
    
    def search_by_role(self, role_pattern: str) -> List[Dict[str, Any]]:
        query = """
        SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
        FROM ApplicationDetail ad 
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id 
        WHERE ad.application_role LIKE %s
        ORDER BY ad.detail_id DESC
        """
        result = self.db.execute_query(query, (f"%{role_pattern}%",))
        return result if result else []
    
    def update(self, detail_id: int, data: Dict[str, Any]) -> Optional[int]:
        try:
            fields = ", ".join([f"{key} = %({key})s" for key in data.keys()])
            query = f"UPDATE ApplicationDetail SET {fields} WHERE detail_id = %(detail_id)s"
            data['detail_id'] = detail_id
            return self.db.execute_query(query, data)
        except Exception as e:
            print(f"[-] Error updating application detail: {e}")
            return None
    
    def delete(self, detail_id: int) -> Optional[int]:
        query = "DELETE FROM ApplicationDetail WHERE detail_id = %s"
        return self.db.execute_query(query, (detail_id,))

class _DatabaseManager:
    def __init__(self) -> None:
        try:
            self.db_connection = _DatabaseConnection()
            self.applicant_profile: Optional[_ApplicantProfile] = None
            self.application_detail: Optional[_ApplicationDetail] = None
            self.auto_decrypt: Optional[_AutoDecryptHelper] = None
        except Exception as e:
            print(f"[-] Error initializing DatabaseManager: {e}")
            raise
    
    def initialize(self) -> bool:
        try:
            if not self.db_connection.connect():
                return False
            
            self.applicant_profile = _ApplicantProfile(self.db_connection)
            self.application_detail = _ApplicationDetail(self.db_connection)
            self.auto_decrypt = _AutoDecryptHelper(self.db_connection)
            
            print("[+] Database initialized successfully")
            return True
        except Exception as e:
            print(f"[-] Error initializing database: {e}")
            return False
    
    def get_data_by_applicant_id(self, applicant_id: int) -> Optional[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return None
            
            if not isinstance(applicant_id, int) or applicant_id <= 0:
                print(f"[-] Invalid applicant ID: {applicant_id}")
                return None
            
            profile_data = self.applicant_profile.get_by_id(applicant_id)
            if not profile_data:
                return Nonege
            
            if self.auto_decrypt:
                applicant_profile = self.auto_decrypt.process_profile_data(profile_data)
            else:
                applicant_profile = profile_data
            
            query = """
            SELECT detail_id, application_role, cv_path
            FROM ApplicationDetail 
            WHERE applicant_id = %s
            ORDER BY detail_id ASC
            """
            
            application_details = self.db_connection.execute_query(query, (applicant_id,))
            if application_details is None:
                application_details = []

            complete_data = {
                'applicant_profile': applicant_profile,
                'application_details': application_details,
                'total_applications': len(application_details)
            }
            
            return complete_data
            
        except Exception as e:
            print(f"[-] Error getting data for applicant ID {applicant_id}: {e}")
            return None
    
    def get_all_applicants_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []
            
            query = """
            SELECT 
                ap.applicant_id,
                ap.first_name,
                ap.last_name, 
                ap.date_of_birth,
                ap.address,
                ap.phone_number,
                ad.detail_id,
                ad.application_role,
                ad.cv_path
            FROM ApplicantProfile ap
            LEFT JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            ORDER BY ap.applicant_id ASC, ad.detail_id ASC
            """
            
            if limit:
                query = f"""
                SELECT 
                    ap.applicant_id,
                    ap.first_name,
                    ap.last_name, 
                    ap.date_of_birth,
                    ap.address,
                    ap.phone_number,
                    ad.detail_id,
                    ad.application_role,
                    ad.cv_path
                FROM (
                    SELECT * FROM ApplicantProfile 
                    ORDER BY applicant_id ASC 
                    LIMIT {limit}
                ) ap
                LEFT JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
                ORDER BY ap.applicant_id ASC, ad.detail_id ASC
                """
            
            result = self.db_connection.execute_query(query)
            if not result:
                return []
            
            applicants_dict = {}
            
            for row in result:
                applicant_id = row['applicant_id']
                
                if applicant_id not in applicants_dict:
                    if self.auto_decrypt:
                        profile_data = {
                            'applicant_id': applicant_id,
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'date_of_birth': row['date_of_birth'],
                            'address': row['address'],
                            'phone_number': row['phone_number']
                        }
                        decrypted_profile = self.auto_decrypt.process_profile_data(profile_data)
                    else:
                        decrypted_profile = {
                            'applicant_id': applicant_id,
                            'first_name': str(row['first_name']) if row['first_name'] else '',
                            'last_name': str(row['last_name']) if row['last_name'] else '',
                            'date_of_birth': str(row['date_of_birth']) if row['date_of_birth'] else '',
                            'address': str(row['address']) if row['address'] else '',
                            'phone_number': str(row['phone_number']) if row['phone_number'] else ''
                        }
                    
                    applicants_dict[applicant_id] = {
                        'applicant_profile': decrypted_profile,
                        'application_details': [],
                        'total_applications': 0
                    }
                
                if row['detail_id'] is not None:
                    application_detail = {
                        'detail_id': row['detail_id'],
                        'application_role': row['application_role'],
                        'cv_path': row['cv_path']
                    }
                    applicants_dict[applicant_id]['application_details'].append(application_detail)
                    applicants_dict[applicant_id]['total_applications'] += 1
            
            return list(applicants_dict.values())
            
        except Exception as e:
            print(f"[-] Error getting all applicants data: {e}")
            return []
    
    def search_applicants_by_name(self, search_term: str) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []

            profiles = self.applicant_profile.get_all()
            if not profiles:
                return []
            
            search_term_lower = search_term.lower()
            matching_applicant_ids = []
            
            for profile in profiles:
                if self.auto_decrypt:
                    decrypted_profile = self.auto_decrypt.process_profile_data(profile)
                    searchable_text = (
                        decrypted_profile['first_name'].lower() + " " +
                        decrypted_profile['last_name'].lower()
                    )
                else:
                    searchable_text = (
                        str(profile['first_name']).lower() + " " +
                        str(profile['last_name']).lower()
                    )
                
                if search_term_lower in searchable_text:
                    matching_applicant_ids.append(profile['applicant_id'])
            
            matching_applicants_data = []
            for applicant_id in matching_applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error searching applicants by name: {e}")
            return []
    
    def get_applicants_by_role(self, role_pattern: str) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []

            query = """
            SELECT DISTINCT applicant_id FROM ApplicationDetail 
            WHERE application_role LIKE %s
            ORDER BY applicant_id ASC
            """
            
            result = self.db_connection.execute_query(query, (f"%{role_pattern}%",))
            if not result:
                return []
            
            applicant_ids = [row['applicant_id'] for row in result]

            matching_applicants_data = []
            for applicant_id in applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error getting applicants by role: {e}")
            return []
    
    def get_applicants_by_cv_path(self, cv_pattern: str) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []
            
            query = """
            SELECT DISTINCT applicant_id FROM ApplicationDetail 
            WHERE cv_path LIKE %s
            ORDER BY applicant_id ASC
            """
            
            result = self.db_connection.execute_query(query, (f"%{cv_pattern}%",))
            if not result:
                return []
            
            applicant_ids = [row['applicant_id'] for row in result]

            matching_applicants_data = []
            for applicant_id in applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error getting applicants by CV path: {e}")
            return []
    
    def get_applicants_by_birth_date(self, birth_date_pattern: str) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []

            profiles = self.applicant_profile.get_all()
            if not profiles:
                return []
            
            matching_applicant_ids = []
            
            for profile in profiles:
                if self.auto_decrypt:
                    decrypted_profile = self.auto_decrypt.process_profile_data(profile)
                    birth_date = decrypted_profile['date_of_birth']
                else:
                    birth_date = str(profile['date_of_birth']) if profile['date_of_birth'] else ""
                
                if birth_date_pattern in birth_date:
                    matching_applicant_ids.append(profile['applicant_id'])

            matching_applicants_data = []
            for applicant_id in matching_applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error getting applicants by birth date: {e}")
            return []
    
    def get_applicants_by_phone(self, phone_pattern: str) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []
            
            profiles = self.applicant_profile.get_all()
            if not profiles:
                return []
            
            matching_applicant_ids = []
            
            for profile in profiles:
                if self.auto_decrypt:
                    decrypted_profile = self.auto_decrypt.process_profile_data(profile)
                    phone_number = decrypted_profile['phone_number']
                else:
                    phone_number = str(profile['phone_number']) if profile['phone_number'] else ""
                
                if phone_pattern in phone_number:
                    matching_applicant_ids.append(profile['applicant_id'])

            matching_applicants_data = []
            for applicant_id in matching_applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error getting applicants by phone: {e}")
            return []
    
    def get_applicants_by_address(self, address_pattern: str) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []
            
            profiles = self.applicant_profile.get_all()
            if not profiles:
                return []
            
            matching_applicant_ids = []
            
            for profile in profiles:
                if self.auto_decrypt:
                    decrypted_profile = self.auto_decrypt.process_profile_data(profile)
                    address = decrypted_profile['address'].lower()
                else:
                    address = str(profile['address']).lower() if profile['address'] else ""
                
                if address_pattern.lower() in address:
                    matching_applicant_ids.append(profile['applicant_id'])

            matching_applicants_data = []
            for applicant_id in matching_applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error getting applicants by address: {e}")
            return []
    
    def advanced_search(self, search_criteria: Dict[str, str]) -> List[Dict[str, Any]]:
        try:
            if not self.db_connection.connection:
                print("[-] No database connection")
                return []

            all_applicants = self.get_all_applicants_data()
            if not all_applicants:
                return []
            
            matching_applicants = []
            
            for applicant in all_applicants:
                profile = applicant['applicant_profile']
                applications = applicant['application_details']

                matches = True
                
                # Name criteria
                if 'name' in search_criteria and search_criteria['name']:
                    full_name = f"{profile['first_name']} {profile['last_name']}".lower()
                    if search_criteria['name'].lower() not in full_name:
                        matches = False
                
                # Birth date criteria
                if 'birth_date' in search_criteria and search_criteria['birth_date']:
                    if search_criteria['birth_date'] not in profile['date_of_birth']:
                        matches = False
                
                # Phone criteria
                if 'phone' in search_criteria and search_criteria['phone']:
                    if search_criteria['phone'] not in profile['phone_number']:
                        matches = False
                
                # Address criteria
                if 'address' in search_criteria and search_criteria['address']:
                    if search_criteria['address'].lower() not in profile['address'].lower():
                        matches = False
                
                # Role criteria (check any application)
                if 'role' in search_criteria and search_criteria['role']:
                    role_found = False
                    for app in applications:
                        if app['application_role'] and search_criteria['role'].lower() in app['application_role'].lower():
                            role_found = True
                            break
                    if not role_found:
                        matches = False
                
                # CV path criteria (check any application)
                if 'cv_path' in search_criteria and search_criteria['cv_path']:
                    cv_found = False
                    for app in applications:
                        if app['cv_path'] and search_criteria['cv_path'].lower() in app['cv_path'].lower():
                            cv_found = True
                            break
                    if not cv_found:
                        matches = False
                
                if matches:
                    matching_applicants.append(applicant)
            
            return matching_applicants
            
        except Exception as e:
            print(f"[-] Error in advanced search: {e}")
            return []
    
    def get_applicants_by_age_range(self, min_age: int, max_age: int) -> List[Dict[str, Any]]:
        try:
            from datetime import datetime
            current_year = datetime.now().year
            
            min_birth_year = current_year - max_age
            max_birth_year = current_year - min_age
            
            profiles = self.applicant_profile.get_all()
            if not profiles:
                return []
            
            matching_applicant_ids = []
            
            for profile in profiles:
                if self.auto_decrypt:
                    decrypted_profile = self.auto_decrypt.process_profile_data(profile)
                    birth_date = decrypted_profile['date_of_birth']
                else:
                    birth_date = str(profile['date_of_birth']) if profile['date_of_birth'] else ""

                try:
                    import re
                    year_match = re.search(r'\b(19|20)\d{2}\b', birth_date)
                    if year_match:
                        birth_year = int(year_match.group())
                        if min_birth_year <= birth_year <= max_birth_year:
                            matching_applicant_ids.append(profile['applicant_id'])
                except (ValueError, AttributeError):
                    continue

            matching_applicants_data = []
            for applicant_id in matching_applicant_ids:
                applicant_data = self.get_data_by_applicant_id(applicant_id)
                if applicant_data:
                    matching_applicants_data.append(applicant_data)
            
            return matching_applicants_data
            
        except Exception as e:
            print(f"[-] Error getting applicants by age range: {e}")
            return []
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        try:
            if not self.auto_decrypt:
                return {'error': 'Auto-decrypt helper not available'}
            
            query = "SELECT * FROM ApplicantProfile"
            result = self.db_connection.execute_query(query)
            
            if not result:
                return {'total_records': 0}
            
            stats = {
                'total_records': len(result),
                'encrypted_fields': 0,
                'plain_text_fields': 0,
                'field_stats': {
                    'first_name': {'encrypted': 0, 'plain_text': 0},
                    'last_name': {'encrypted': 0, 'plain_text': 0},
                    'date_of_birth': {'encrypted': 0, 'plain_text': 0},
                    'address': {'encrypted': 0, 'plain_text': 0},
                    'phone_number': {'encrypted': 0, 'plain_text': 0}
                }
            }
            
            for profile in result:
                fields_to_check = ['first_name', 'last_name', 'date_of_birth', 'address', 'phone_number']
                
                for field in fields_to_check:
                    field_value = str(profile[field]) if profile[field] else ""
                    is_encrypted = self.auto_decrypt.is_data_encrypted(field_value)
                    
                    if is_encrypted:
                        stats['encrypted_fields'] += 1
                        stats['field_stats'][field]['encrypted'] += 1
                    else:
                        stats['plain_text_fields'] += 1
                        stats['field_stats'][field]['plain_text'] += 1
            
            return stats
            
        except Exception as e:
            print(f"[-] Error getting encryption statistics: {e}")
            return {'error': str(e)}
    
    def close(self) -> None:
        try:
            self.db_connection.disconnect()
        except Exception as e:
            print(f"[-] Error closing database: {e}")

# Singleton instance:
db_manager = _DatabaseManager()

# Public API:
__all__ = ["db_manager"]
