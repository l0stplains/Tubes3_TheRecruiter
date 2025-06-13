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
        print(f"[*] Looking for config.py in: {current_dir}")
        sys.exit(1)

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
        except Exception as e:
            print(f"[-] Error initializing DatabaseManager: {e}")
            raise
    
    def initialize(self) -> bool:
        try:
            if not self.db_connection.connect():
                return False
            
            self.applicant_profile = ApplicantProfile(self.db_connection)
            self.application_detail = ApplicationDetail(self.db_connection)
            
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