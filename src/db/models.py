import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any

class DatabaseConnection:
    def __init__(self, host='localhost', database='ats_system', user='gongyoo', password='roulette', port=2025):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                autocommit=True
            )
            if self.connection.is_connected():
                print(f"Connected to MySQL database: {self.database}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
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
            print(f"Error executing query: {e}")
            return None

class ApplicantProfile:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS ApplicantProfile (
            applicant_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) DEFAULT NULL,
            last_name VARCHAR(50) DEFAULT NULL,
            date_of_birth DATE DEFAULT NULL,
            address VARCHAR(255) DEFAULT NULL,
            phone_number VARCHAR(20) DEFAULT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        return self.db.execute_query(query)
    
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
        query = "SELECT * FROM ApplicantProfile"
        return self.db.execute_query(query) or []

class ApplicationDetail:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS ApplicationDetail (
            detail_id INT AUTO_INCREMENT PRIMARY KEY,
            applicant_id INT NOT NULL,
            application_role VARCHAR(100) DEFAULT NULL,
            cv_path TEXT NOT NULL,
            FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        return self.db.execute_query(query)
    
    def insert(self, data: Dict[str, Any]):
        query = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
        VALUES (%(applicant_id)s, %(application_role)s, %(cv_path)s)
        """
        return self.db.execute_query(query, data)
    
    def get_by_id(self, detail_id: int):
        query = """
        SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
        FROM ApplicationDetail ad 
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id 
        WHERE ad.detail_id = %s
        """
        result = self.db.execute_query(query, (detail_id,))
        return result[0] if result else None
    
    def get_all_with_profiles(self):
        query = """
        SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
        FROM ApplicationDetail ad 
        JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
        """
        return self.db.execute_query(query) or []

class DatabaseManager:
    def __init__(self, **connection_params):
        self.db_connection = DatabaseConnection(**connection_params)
        self.applicant_profile = None
        self.application_detail = None
    
    def initialize(self):
        if not self.db_connection.connect():
            return False
        
        self.applicant_profile = ApplicantProfile(self.db_connection)
        self.application_detail = ApplicationDetail(self.db_connection)
        
        # Create tables
        self.applicant_profile.create_table()
        self.application_detail.create_table()
        print("Database tables created successfully")
        return True
    
    def close(self):
        self.db_connection.disconnect()

# Test
if __name__ == "__main__":
    db_manager = DatabaseManager(
        host='localhost',
        database='ats_system',
        user='gongyoo',
        password='roulette',
        port=2025
    )
    
    if db_manager.initialize():
        print("Database setup complete!")
        db_manager.close()
    else:
        print("Database setup failed!")