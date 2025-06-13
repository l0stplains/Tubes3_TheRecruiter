import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any

# relative
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
db_dir = os.path.join(src_dir, 'db')
utils_dir = os.path.join(src_dir, 'utils')

sys.path.extend([src_dir, db_dir, utils_dir])

# Import dependencies, make sure they are installed :3
try:
    import mysql.connector
    from mysql.connector import Error
except ImportError as e:
    print(f"[-] Error importing mysql.connector: {e}")
    print("[*] Install with: pip install mysql-connector-python")
    sys.exit(1)

try:
    from faker import Faker
except ImportError as e:
    print(f"[-] Error importing faker: {e}")
    print("[*] Install with: pip install faker")
    sys.exit(1)

try:
    from config import get_db_config
except ImportError:
    print("[-] Error: Cannot find config module")
    print(f"[*] Looking for config.py in: {db_dir}")
    print(f"[*] Make sure config.py exists in src/db/ directory")
    sys.exit(1)

class DatabaseSeeder:
    def __init__(self) -> None:
        try:
            config = get_db_config()
            self.params: Dict[str, Any] = config.get_connection_params()
        except Exception as e:
            print(f"[-] Error loading database config: {e}")
            sys.exit(1)
            
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.fake = Faker('en_US')

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

    def generate_phone_number(self) -> str:
        area = self.fake.random_int(min=100, max=999)
        first = self.fake.random_int(min=100, max=999)
        last = self.fake.random_int(min=1000, max=9999)
        return f"+1-{area}-{first}-{last}"

    def generate_birth_date(self) -> datetime:
        return self.fake.date_of_birth(minimum_age=22, maximum_age=60)

    def generate_address(self) -> str:
        address = self.fake.address().replace('\n', ', ')
        return address[:255]

    def clear_existing_data(self) -> bool:
        try:
            if not self.connection:
                print("[-] No database connection")
                return False
                
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ApplicantProfile")
            cursor.execute("ALTER TABLE ApplicantProfile AUTO_INCREMENT = 1")
            self.connection.commit()
            cursor.close()
            print("[+] Cleared existing ApplicantProfile data")
            return True
        except Error as e:
            print(f"[-] Error clearing data: {e}")
            return False
        except Exception as e:
            print(f"[-] Unexpected error clearing data: {e}")
            return False

    def seed_applicant_profiles(self, count: int = 200) -> bool:
        try:
            if not self.connection:
                print("[-] No database connection")
                return False
                
            cursor = self.connection.cursor()
            
            print(f"[*] Generating and inserting {count} realistic applicant profiles...")
            
            query = """
            INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for i in range(count):
                first_name = self.fake.first_name()[:50]
                last_name = self.fake.last_name()[:50]
                birth_date = self.generate_birth_date()
                address = self.generate_address()
                phone = self.generate_phone_number()
                
                applicant_data = (first_name, last_name, birth_date, address, phone)
                cursor.execute(query, applicant_data)
                
                if (i + 1) % 50 == 0:
                    self.connection.commit()
                    print(f"[*] Inserted {i + 1}/{count} profiles...")
            
            self.connection.commit()
            cursor.close()
            
            print(f"[+] Successfully seeded {count} applicant profiles")
            return True
            
        except Error as e:
            print(f"[-] Error seeding applicant profiles: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return False
        except Exception as e:
            print(f"[-] Unexpected error seeding data: {e}")
            return False

    def verify_seeded_data(self) -> None:
        try:
            if not self.connection:
                print("[-] No database connection")
                return
                
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM ApplicantProfile")
            result = cursor.fetchone()
            total_count = result['total'] if result else 0
            
            cursor.execute("SELECT * FROM ApplicantProfile LIMIT 5")
            sample_data = cursor.fetchall()
            cursor.close()
            
            print(f"\n[+] Verification Results:")
            print(f"    Total ApplicantProfile records: {total_count}")
            print(f"\n[+] Sample data (first 5 records):")
            
            for record in sample_data:
                print(f"    ID: {record['applicant_id']}, "
                      f"Name: {record['first_name']} {record['last_name']}, "
                      f"DOB: {record['date_of_birth']}, "
                      f"Phone: {record['phone_number']}")
                      
        except Error as e:
            print(f"[-] Error verifying data: {e}")
        except Exception as e:
            print(f"[-] Unexpected error verifying data: {e}")


def main() -> None:
    print("Hewwo :3")
    print("="*10)
    
    try:
        seeder = DatabaseSeeder()
        
        if not seeder.connect():
            print("[-] Failed to connect to database. Please check your configuration.")
            return
        
        clear_data = input("Do you want to clear existing ApplicantProfile data? (y/N): ").lower().strip()
        if clear_data == 'y':
            seeder.clear_existing_data()
        
        try:
            count_input = input("Enter number of applicant profiles to create (default: 200): ").strip()
            count = int(count_input) if count_input else 200
            if count <= 0:
                count = 200
        except ValueError:
            count = 200
            print("[*] Invalid input, using default count of 200")
        
        print(f"\n[*] Creating {count} applicant profiles...")
        
        if seeder.seed_applicant_profiles(count):
            seeder.verify_seeded_data()
            print(f"\n[+] Seeding process completed successfully!")
        else:
            print(f"\n[-] Seeding process failed!")
        
    except KeyboardInterrupt:
        print("\n[-] Seeding process interrupted by user")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
    finally:
        try:
            seeder.disconnect()
        except:
            pass

if __name__ == "__main__":
    main()