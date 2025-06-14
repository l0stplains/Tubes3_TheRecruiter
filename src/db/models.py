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

class DatabaseConnection:
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

class DecryptionHelper:
    def __init__(self, db_connection: DatabaseConnection) -> None:
        self.db = db_connection
        self.encryption_key: Optional[bytes] = None

        try:
            config = get_db_config()
            encryption_password = config.get_encryption_password()
            if encryption_password and decrypt is not None:
                self.set_encryption_key(encryption_password)
                print(f"[+] Decryption key loaded from configuration")
            else:
                print("[*] No encryption password found in configuration")
        except Exception as e:
            print(f"[-] Error loading encryption key from config: {e}")
    
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
            print(f"[+] Encryption key set successfully")
            return True
        except Exception as e:
            print(f"[-] Error setting encryption key: {e}")
            return False
    
    def is_data_encrypted(self, text: str) -> bool:
        try:
            if not text or len(text) < 10:
                return False
            bytes.fromhex(text)
            return True
        except (ValueError, TypeError):
            return False
    
    def decrypt_text(self, encrypted_text: str) -> str:
        try:
            if self.encryption_key is None or decrypt is None:
                return encrypted_text
            
            if not self.is_data_encrypted(encrypted_text):
                return encrypted_text
            
            encrypted_bytes = bytes.fromhex(encrypted_text)
            decrypted_bytes = decrypt(self.encryption_key, encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"[-] Error decrypting text: {e}")
            return encrypted_text
    
    def get_decrypted_applicant_profiles(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            query = "SELECT * FROM ApplicantProfile"
            if limit:
                query += f" LIMIT {limit}"
            
            result = self.db.execute_query(query)
            if not result:
                return []
            
            if self.encryption_key is None:
                print("[*] No encryption key set, returning raw data")
                return result
            
            decrypted_profiles = []
            for profile in result:
                decrypted_profile = {
                    'applicant_id': profile['applicant_id'],
                    'first_name': self.decrypt_text(profile['first_name']),
                    'last_name': self.decrypt_text(profile['last_name']),
                    'date_of_birth': self.decrypt_text(str(profile['date_of_birth'])),
                    'address': self.decrypt_text(profile['address']),
                    'phone_number': self.decrypt_text(profile['phone_number']),

                    'was_encrypted': {
                        'first_name': self.is_data_encrypted(profile['first_name']),
                        'last_name': self.is_data_encrypted(profile['last_name']),
                        'date_of_birth': self.is_data_encrypted(str(profile['date_of_birth'])),
                        'address': self.is_data_encrypted(profile['address']),
                        'phone_number': self.is_data_encrypted(profile['phone_number'])
                    }
                }
                decrypted_profiles.append(decrypted_profile)
            
            return decrypted_profiles
            
        except Exception as e:
            print(f"[-] Error getting decrypted profiles: {e}")
            return []
    
    def get_decrypted_applicant_by_id(self, applicant_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = "SELECT * FROM ApplicantProfile WHERE applicant_id = %s"
            result = self.db.execute_query(query, (applicant_id,))
            
            if not result or len(result) == 0:
                return None
            
            profile = result[0]
            
            if self.encryption_key is None:
                print("[*] No encryption key set, returning raw data")
                return profile
            
            decrypted_profile = {
                'applicant_id': profile['applicant_id'],
                'first_name': self.decrypt_text(profile['first_name']),
                'last_name': self.decrypt_text(profile['last_name']),
                'date_of_birth': self.decrypt_text(str(profile['date_of_birth'])),
                'address': self.decrypt_text(profile['address']),
                'phone_number': self.decrypt_text(profile['phone_number']),

                'was_encrypted': {
                    'first_name': self.is_data_encrypted(profile['first_name']),
                    'last_name': self.is_data_encrypted(profile['last_name']),
                    'date_of_birth': self.is_data_encrypted(str(profile['date_of_birth'])),
                    'address': self.is_data_encrypted(profile['address']),
                    'phone_number': self.is_data_encrypted(profile['phone_number'])
                }
            }
            
            return decrypted_profile
            
        except Exception as e:
            print(f"[-] Error getting decrypted profile for ID {applicant_id}: {e}")
            return None
    
    def search_decrypted_profiles(self, search_term: str) -> List[Dict[str, Any]]:
        try:
            all_profiles = self.get_decrypted_applicant_profiles()
            
            if not all_profiles:
                return []
            
            search_term_lower = search_term.lower()
            matching_profiles = []
            
            for profile in all_profiles:
                searchable_text = (
                    profile['first_name'].lower() + " " +
                    profile['last_name'].lower() + " " +
                    profile['address'].lower() + " " +
                    profile['phone_number'].lower()
                )
                
                if search_term_lower in searchable_text:
                    matching_profiles.append(profile)
            
            return matching_profiles
            
        except Exception as e:
            print(f"[-] Error searching decrypted profiles: {e}")
            return []
    
    def get_encryption_statistics(self) -> Dict[str, Any]:
        try:
            query = "SELECT * FROM ApplicantProfile"
            result = self.db.execute_query(query)
            
            if not result:
                return {'total_records': 0}
            
            stats = {
                'total_records': len(result),
                'encrypted_records': 0,
                'plain_text_records': 0,
                'mixed_records': 0,
                'field_encryption_stats': {
                    'first_name': {'encrypted': 0, 'plain_text': 0},
                    'last_name': {'encrypted': 0, 'plain_text': 0},
                    'date_of_birth': {'encrypted': 0, 'plain_text': 0},
                    'address': {'encrypted': 0, 'plain_text': 0},
                    'phone_number': {'encrypted': 0, 'plain_text': 0}
                }
            }
            
            for profile in result:
                encrypted_fields = 0
                fields_to_check = ['first_name', 'last_name', 'date_of_birth', 'address', 'phone_number']
                
                for field in fields_to_check:
                    field_value = str(profile[field]) if profile[field] else ""
                    is_encrypted = self.is_data_encrypted(field_value)
                    
                    if is_encrypted:
                        encrypted_fields += 1
                        stats['field_encryption_stats'][field]['encrypted'] += 1
                    else:
                        stats['field_encryption_stats'][field]['plain_text'] += 1

                if encrypted_fields == len(fields_to_check):
                    stats['encrypted_records'] += 1
                elif encrypted_fields == 0:
                    stats['plain_text_records'] += 1
                else:
                    stats['mixed_records'] += 1
            
            return stats
            
        except Exception as e:
            print(f"[-] Error getting encryption statistics: {e}")
            return {'error': str(e)}

class ApplicantProfile:
    def __init__(self, db_connection: DatabaseConnection) -> None:
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

class ApplicationDetail:
    def __init__(self, db_connection: DatabaseConnection) -> None:
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

class DatabaseManager:
    def __init__(self) -> None:
        try:
            self.db_connection = DatabaseConnection()
            self.applicant_profile: Optional[ApplicantProfile] = None
            self.application_detail: Optional[ApplicationDetail] = None
            self.decryption_helper: Optional[DecryptionHelper] = None
        except Exception as e:
            print(f"[-] Error initializing DatabaseManager: {e}")
            raise
    
    def initialize(self) -> bool:
        try:
            if not self.db_connection.connect():
                return False
            
            self.applicant_profile = ApplicantProfile(self.db_connection)
            self.application_detail = ApplicationDetail(self.db_connection)
            self.decryption_helper = DecryptionHelper(self.db_connection)
            
            print("[+] Database initialized successfully")
            return True
        except Exception as e:
            print(f"[-] Error initializing database: {e}")
            return False
    
    def close(self) -> None:
        try:
            self.db_connection.disconnect()
        except Exception as e:
            print(f"[-] Error closing database: {e}")