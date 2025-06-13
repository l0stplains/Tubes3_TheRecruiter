import sys
import os
import random
from datetime import datetime
from typing import Optional, Dict, Any, List

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
    import fitz
except ImportError as e:
    print(f"[-] Error importing faker or PyMuPDF: {e}")
    print("[*] Install with: pip install faker pymupdf")
    sys.exit(1)

try:
    from config import get_db_config
except ImportError:
    print("[-] Error: Cannot find config module")
    print(f"[*] Looking for config.py in: {db_dir}")
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
        self.data_folder = os.path.join(project_root, 'data')
        
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            print(f"[*] Created data folder: {self.data_folder}")

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

    def extract_role_from_pdf(self, pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                page = doc[0]
                text = page.get_text()
                lines = text.strip().split('\n')
                if lines:
                    first_line = lines[0].strip()
                    if len(first_line) > 100:
                        first_line = first_line[:100]
                    doc.close()
                    return first_line if first_line else "Unknown Role"
            doc.close()
            return "Unknown Role"
        except Exception as e:
            print(f"[-] Error reading PDF {pdf_path}: {e}")
            return "Unknown Role"

    def get_pdf_files(self) -> List[str]:
        try:
            pdf_files = []
            if os.path.exists(self.data_folder):
                for file in os.listdir(self.data_folder):
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(file)
            return pdf_files
        except Exception as e:
            print(f"[-] Error reading data folder: {e}")
            return []

    def get_applicant_ids(self) -> List[int]:
        try:
            if not self.connection:
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT applicant_id FROM ApplicantProfile")
            ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return ids
        except Exception as e:
            print(f"[-] Error getting applicant IDs: {e}")
            return []

    def clear_existing_data(self) -> bool:
        try:
            if not self.connection:
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

    def clear_existing_application_data(self) -> bool:
        try:
            if not self.connection:
                return False
                
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ApplicationDetail")
            cursor.execute("ALTER TABLE ApplicationDetail AUTO_INCREMENT = 1")
            self.connection.commit()
            cursor.close()
            print("[+] Cleared existing ApplicationDetail data")
            return True
        except Error as e:
            print(f"[-] Error clearing application data: {e}")
            return False

    def seed_applicant_profiles(self, count: int = 200) -> bool:
        try:
            if not self.connection:
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

    def seed_application_details(self) -> bool:
        try:
            if not self.connection:
                return False
            
            pdf_files = self.get_pdf_files()
            applicant_ids = self.get_applicant_ids()
            
            if not pdf_files:
                print("[-] No PDF files found in data folder")
                return False
            
            if not applicant_ids:
                print("[-] No applicants found in database")
                return False
            
            print(f"[*] Found {len(pdf_files)} PDF files")
            print(f"[*] Found {len(applicant_ids)} applicants")
            
            cursor = self.connection.cursor()
            query = """
            INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
            VALUES (%s, %s, %s)
            """
            
            inserted_count = 0
            
            for applicant_id in applicant_ids:
                num_applications = random.randint(1, 3)
                selected_pdfs = random.sample(pdf_files, min(num_applications, len(pdf_files)))
                
                for pdf_file in selected_pdfs:
                    pdf_path = os.path.join(self.data_folder, pdf_file)
                    role = self.extract_role_from_pdf(pdf_path)
                    
                    application_data = (applicant_id, role, pdf_file)
                    cursor.execute(query, application_data)
                    inserted_count += 1
                    
                    if inserted_count % 50 == 0:
                        self.connection.commit()
                        print(f"[*] Inserted {inserted_count} applications...")
            
            self.connection.commit()
            cursor.close()
            print(f"[+] Successfully seeded {inserted_count} application details")
            return True
            
        except Error as e:
            print(f"[-] Error seeding application details: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return False

    def verify_seeded_data(self) -> None:
        try:
            if not self.connection:
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

    def verify_application_data(self) -> None:
        try:
            if not self.connection:
                return
                
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM ApplicationDetail")
            result = cursor.fetchone()
            total_count = result['total'] if result else 0
            
            cursor.execute("""
                SELECT ad.detail_id, ad.application_role, ad.cv_path,
                       ap.first_name, ap.last_name
                FROM ApplicationDetail ad 
                JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
                LIMIT 5
            """)
            sample_data = cursor.fetchall()
            cursor.close()
            
            print(f"\n[+] Application Verification Results:")
            print(f"    Total ApplicationDetail records: {total_count}")
            print(f"\n[+] Sample application data (first 5 records):")
            
            for record in sample_data:
                print(f"    ID: {record['detail_id']}, "
                      f"Applicant: {record['first_name']} {record['last_name']}, "
                      f"Role: {record['application_role'][:50]}..., "
                      f"CV: {record['cv_path']}")
                      
        except Error as e:
            print(f"[-] Error verifying application data: {e}")



def main() -> None:
    print("DATABASE SEEDER FOR ATS SYSTEM")
    print("="*50)
    
    try:
        seeder = DatabaseSeeder()
        
        if not seeder.connect():
            print("[-] Failed to connect to database. Please check your configuration.")
            return
        
        print("\nSelect seeding option:")
        print("1. Seed ApplicantProfile only")
        print("2. Seed ApplicationDetail only")
        print("3. Seed both ApplicantProfile and ApplicationDetail")
        print("4. Clear all data")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            clear_data = input("Clear existing ApplicantProfile data? (y/N): ").lower().strip()
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
                print(f"\n[+] Applicant seeding completed successfully!")
                
        elif choice == '2':
            clear_data = input("Clear existing ApplicationDetail data? (y/N): ").lower().strip()
            if clear_data == 'y':
                seeder.clear_existing_application_data()
            
            print(f"\n[*] Creating application details from PDF files...")
            if seeder.seed_application_details():
                seeder.verify_application_data()
                print(f"\n[+] Application detail seeding completed successfully!")
                
        elif choice == '3':
            clear_data = input("Clear all existing data? (y/N): ").lower().strip()
            if clear_data == 'y':
                seeder.clear_existing_application_data()
                seeder.clear_existing_data()
            
            try:
                count_input = input("Enter number of applicant profiles to create (default: 200): ").strip()
                count = int(count_input) if count_input else 200
                if count <= 0:
                    count = 200
            except ValueError:
                count = 200
                print("[*] Invalid input, using default count of 200")
            
            print(f"\n[*] Step 1: Creating {count} applicant profiles...")
            if seeder.seed_applicant_profiles(count):
                seeder.verify_seeded_data()
                
                print(f"\n[*] Step 2: Creating application details from PDF files...")
                if seeder.seed_application_details():
                    seeder.verify_application_data()
                    print(f"\n[+] Complete seeding process finished successfully!")
                    
        elif choice == '4':
            confirm = input("Are you sure you want to clear ALL data? (y/N): ").lower().strip()
            if confirm == 'y':
                seeder.clear_existing_application_data()
                seeder.clear_existing_data()
                print("[+] All data cleared successfully!")
        else:
            print("Invalid choice. Please select 1-4.")
        
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