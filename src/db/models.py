import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from config import get_db_config
except ImportError:
    # Try importing from utils directory (fallback)
    utils_dir = os.path.join(os.path.dirname(current_dir), 'utils')
    sys.path.insert(0, utils_dir)
    try:
        from config import get_db_config
    except ImportError:
        print("[-] Error: Cannot find config module")
        print(f"[*] Looking for config.py in: {current_dir}")
        print(f"[*] Make sure config.py exists in the same directory as models.py")
        sys.exit(1)

class DatabaseConnection:
    def __init__(self):
        config = get_db_config()
        self.params = config.get_connection_params()
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.params)
            if self.connection.is_connected():
                print(f"[+] Connected to database: {self.params['database']}")
                return True
        except Error as e:
            print(f"[-] Database connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[-] Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None):
        try:
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

class ApplicantProfile:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def insert(self, data: Dict[str, Any]):
        query = """
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%(first_name)s, %(last_name)s, %(date_of_birth)s, %(address)s, %(phone_number)s)
        """
        return self.db.execute_query(query, data)
    
    def get_by_id(self, applicant_id: int):
        query = "SELECT * FROM ApplicantProfile WHERE applicant_id = %s"
        result = self.db.execute_query(query, (applicant_id,))
        return result[0] if result else None
    
    def get_all(self):
        query = "SELECT * FROM ApplicantProfile ORDER BY applicant_id DESC"
        return self.db.execute_query(query) or []
    
    def update(self, applicant_id: int, data: Dict[str, Any]):
        fields = ", ".join([f"{key} = %({key})s" for key in data.keys()])
        query = f"UPDATE ApplicantProfile SET {fields} WHERE applicant_id = %(applicant_id)s"
        data['applicant_id'] = applicant_id
        return self.db.execute_query(query, data)
    
    def delete(self, applicant_id: int):
        query = "DELETE FROM ApplicantProfile WHERE applicant_id = %s"
        return self.db.execute_query(query, (applicant_id,))

class ApplicationDetail:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def insert(self, data: Dict[str, Any]):
        query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path, status)
        VALUES (%(applicant_id)s, %(application_role)s, %(cv_path)s, %(status)s)
        """
        return self.db.execute_query(query, data)
    
    def get_all_with_profiles(self):
        query = """
        SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
        FROM ApplicationDetail ad 
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
        ORDER BY ad.detail_id DESC
        """
        return self.db.execute_query(query) or []
    
    def search_by_role(self, role_pattern: str):
        query = """
        SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
        FROM ApplicationDetail ad 
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id 
        WHERE ad.application_role LIKE %s
        ORDER BY ad.detail_id DESC
        """
        return self.db.execute_query(query, (f"%{role_pattern}%",)) or []
    
    def update(self, detail_id: int, data: Dict[str, Any]):
        fields = ", ".join([f"{key} = %({key})s" for key in data.keys()])
        query = f"UPDATE ApplicationDetail SET {fields} WHERE detail_id = %(detail_id)s"
        data['detail_id'] = detail_id
        return self.db.execute_query(query, data)
    
    def delete(self, detail_id: int):
        query = "DELETE FROM ApplicationDetail WHERE detail_id = %s"
        return self.db.execute_query(query, (detail_id,))

class DatabaseManager:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.applicant_profile = None
        self.application_detail = None
    
    def initialize(self):
        if not self.db_connection.connect():
            return False
        
        self.applicant_profile = ApplicantProfile(self.db_connection)
        self.application_detail = ApplicationDetail(self.db_connection)
        
        print("[+] Database initialized successfully")
        return True
    
    def close(self):
        self.db_connection.disconnect()