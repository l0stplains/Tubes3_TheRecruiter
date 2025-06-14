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
except ImportError as e:
    print(f"[-] Error importing faker: {e}")
    print("[*] Install with: pip install faker")
    sys.exit(1)

try:
    from encrypt import encrypt, decrypt
except ImportError:
    print("[-] Warning: encrypt.py not found, encryption features disabled")
    encrypt = None
    decrypt = None

try:
    from config import get_db_config
except ImportError:
    print("[-] Error: Cannot find config module")
    sys.exit(1)

class DatabaseSeeder:
    def __init__(self) -> None:
        try:
            config = get_db_config()
            self.params: Dict[str, Any] = config.get_connection_params()
            
            self.encryption_key: Optional[bytes] = None
            encryption_password = config.get_encryption_password()
            if encryption_password and encrypt is not None:
                self.set_encryption_key(encryption_password)
                print(f"[+] Encryption key loaded from configuration")
            else:
                print("[*] No encryption password found in configuration")
                
        except Exception as e:
            print(f"[-] Error loading database config: {e}")
            sys.exit(1)
            
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.fake = Faker('en_US')
        self.data_folder = os.path.join(project_root, 'data')
        
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

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

    def generate_clean_phone_number(self) -> str:
        area_code = random.randint(200, 999)  # Valid area codes
        exchange = random.randint(200, 999)   # Valid exchange codes  
        number = random.randint(1000, 9999)   # Last 4 digits
        return f"+1-{area_code}-{exchange}-{number}"

    def generate_indonesian_phone_number(self) -> str:
        provider_prefix = random.choice(['811', '812', '813', '821', '822', '823', '851', '852'])
        number = random.randint(10000000, 99999999)
        return f"+62-{provider_prefix}-{str(number)[:4]}-{str(number)[4:]}"

    def generate_phone_number(self) -> str:
        format_choice = random.choice(['us_clean', 'indonesian'])
        
        if format_choice == 'us_clean':
            return self.generate_clean_phone_number()
        else:
            return self.generate_indonesian_phone_number()

    def generate_birth_date(self) -> datetime:
        return self.fake.date_of_birth(minimum_age=19, maximum_age=27)

    def generate_address(self) -> str:
        return self.fake.address().replace('\n', ', ')

    def generate_job_role(self) -> str:
        return self.fake.job()

    def set_encryption_key(self, key_string: str) -> bool:
        try:
            if encrypt is None:
                print("[-] Encryption not available")
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

    def encrypt_data(self, data: str) -> str:
        try:
            if self.encryption_key is None or encrypt is None:
                return data
            
            encrypted_bytes = encrypt(self.encryption_key, data.encode('utf-8'))
            return encrypted_bytes.hex()
        except Exception as e:
            print(f"[-] Error encrypting data: {e}")
            return data

    def decrypt_data(self, hex_data: str) -> str:
        try:
            if self.encryption_key is None or decrypt is None:
                return hex_data
            
            encrypted_bytes = bytes.fromhex(hex_data)
            decrypted_bytes = decrypt(self.encryption_key, encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"[-] Error decrypting data: {e}")
            return hex_data

    def get_pdf_files(self) -> List[str]:
        try:
            pdf_files = []
            if not os.path.exists(self.data_folder):
                return []
            
            for root, dirs, files in os.walk(self.data_folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        relative_path = os.path.relpath(os.path.join(root, file), self.data_folder)
                        pdf_files.append(relative_path)
            
            return pdf_files
        except Exception as e:
            print(f"[-] Error searching for PDF files: {e}")
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
            cursor.execute("DELETE FROM ApplicationDetail")
            cursor.execute("DELETE FROM ApplicantProfile")
            cursor.execute("ALTER TABLE ApplicantProfile AUTO_INCREMENT = 1")
            cursor.execute("ALTER TABLE ApplicationDetail AUTO_INCREMENT = 1")
            self.connection.commit()
            cursor.close()
            print("[+] Cleared all existing data")
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

    def execute_sql_file(self, sql_file_path: str) -> bool:
        try:
            if not self.connection:
                return False
            
            if not os.path.exists(sql_file_path):
                print(f"[-] SQL file not found: {sql_file_path}")
                return False
            
            print(f"[*] Reading SQL file: {sql_file_path}")
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()

            cursor = self.connection.cursor()
            sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            executed_count = 0
            for i, command in enumerate(sql_commands):
                try:
                    if command.upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'SET')):
                        cursor.execute(command)
                        executed_count += 1
                        
                        if executed_count % 50 == 0:
                            self.connection.commit()
                            print(f"[*] Executed {executed_count}/{len(sql_commands)} commands...")
                            
                except Error as e:
                    print(f"[-] Error executing command {i+1}: {e}")
                    print(f"    Command: {command[:100]}...")
                    continue
            
            self.connection.commit()
            cursor.close()
            print(f"[+] Successfully executed {executed_count} SQL commands from file")
            return True
            
        except Exception as e:
            print(f"[-] Error executing SQL file: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return False

    def _is_hex_string(self, text: str) -> bool:
        try:
            if not text or len(text) < 10:
                return False
            bytes.fromhex(text)
            return True
        except (ValueError, TypeError):
            return False

    def backup_database(self) -> bool:
        try:
            if not self.connection:
                return False
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_applicants_{timestamp}.sql"
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ApplicantProfile")
            records = cursor.fetchall()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("-- Database backup created at " + timestamp + "\n")
                f.write("-- ApplicantProfile table backup\n\n")
                
                for record in records:
                    f.write(f"INSERT INTO ApplicantProfile VALUES (")
                    f.write(f"{record['applicant_id']}, ")
                    f.write(f"'{record['first_name'].replace(chr(39), chr(39)+chr(39))}', ")
                    f.write(f"'{record['last_name'].replace(chr(39), chr(39)+chr(39))}', ")
                    f.write(f"'{record['date_of_birth']}', ")
                    f.write(f"'{record['address'].replace(chr(39), chr(39)+chr(39))}', ")
                    f.write(f"'{record['phone_number']}');\n")
            
            cursor.close()
            print(f"[+] Database backup created: {backup_file}")
            return True
            
        except Exception as e:
            print(f"[-] Error creating backup: {e}")
            return False

    def encrypt_existing_data(self) -> bool:
        try:
            if not self.connection:
                return False
            
            if self.encryption_key is None:
                print("[-] Encryption key not set")
                return False
            
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM ApplicantProfile")
            records = cursor.fetchall()
            
            if not records:
                print("[-] No records found to encrypt")
                cursor.close()
                return False
            
            print(f"[*] Found {len(records)} records to encrypt...")
            
            update_query = """
            UPDATE ApplicantProfile 
            SET first_name = %s, last_name = %s, date_of_birth = %s, address = %s, phone_number = %s
            WHERE applicant_id = %s
            """
            
            encrypted_count = 0
            for record in records:
                try:
                    if self._is_hex_string(record['first_name']):
                        print(f"[*] Record ID {record['applicant_id']} appears to be already encrypted, skipping...")
                        continue
                    
                    encrypted_first_name = self.encrypt_data(record['first_name'])
                    encrypted_last_name = self.encrypt_data(record['last_name'])
                    encrypted_birth_date = self.encrypt_data(str(record['date_of_birth']))
                    encrypted_address = self.encrypt_data(record['address'])
                    encrypted_phone = self.encrypt_data(record['phone_number'])
                    
                    cursor.execute(update_query, (
                        encrypted_first_name,
                        encrypted_last_name, 
                        encrypted_birth_date,
                        encrypted_address,
                        encrypted_phone,
                        record['applicant_id']
                    ))
                    
                    encrypted_count += 1
                    
                    if encrypted_count % 20 == 0:
                        self.connection.commit()
                        print(f"[*] Encrypted {encrypted_count}/{len(records)} records...")
                        
                except Exception as e:
                    print(f"[-] Error encrypting record ID {record['applicant_id']}: {e}")
                    continue
            
            self.connection.commit()
            cursor.close()
            print(f"[+] Successfully encrypted {encrypted_count} records")
            return True
            
        except Error as e:
            print(f"[-] Error encrypting existing data: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return False

    def decrypt_existing_data(self) -> bool:
        try:
            if not self.connection:
                return False
            
            if self.encryption_key is None:
                print("[-] Encryption key not set")
                return False
            
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM ApplicantProfile")
            records = cursor.fetchall()
            
            if not records:
                print("[-] No records found to decrypt")
                cursor.close()
                return False
            
            print(f"[*] Found {len(records)} records to decrypt...")

            update_query = """
            UPDATE ApplicantProfile 
            SET first_name = %s, last_name = %s, date_of_birth = %s, address = %s, phone_number = %s
            WHERE applicant_id = %s
            """
            
            decrypted_count = 0
            for record in records:
                try:
                    if not self._is_hex_string(record['first_name']):
                        print(f"[*] Record ID {record['applicant_id']} appears to be plain text, skipping...")
                        continue

                    decrypted_first_name = self.decrypt_data(record['first_name'])
                    decrypted_last_name = self.decrypt_data(record['last_name'])
                    decrypted_birth_date = self.decrypt_data(record['date_of_birth'])
                    decrypted_address = self.decrypt_data(record['address'])
                    decrypted_phone = self.decrypt_data(record['phone_number'])

                    cursor.execute(update_query, (
                        decrypted_first_name,
                        decrypted_last_name,
                        decrypted_birth_date,
                        decrypted_address,
                        decrypted_phone,
                        record['applicant_id']
                    ))
                    
                    decrypted_count += 1
                    
                    if decrypted_count % 20 == 0:
                        self.connection.commit()
                        print(f"[*] Decrypted {decrypted_count}/{len(records)} records...")
                        
                except Exception as e:
                    print(f"[-] Error decrypting record ID {record['applicant_id']}: {e}")
                    continue
            
            self.connection.commit()
            cursor.close()
            print(f"[+] Successfully decrypted {decrypted_count} records")
            return True
            
        except Error as e:
            print(f"[-] Error decrypting existing data: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return False

    def seed_applicant_profiles(self, count: int = 200, use_encryption: bool = False) -> bool:
        try:
            if not self.connection:
                return False
            
            if use_encryption and self.encryption_key is None:
                print("[-] Encryption requested but no key set")
                return False
                
            cursor = self.connection.cursor()
            encryption_status = "with encryption" if use_encryption else "without encryption"
            print(f"[*] Generating and inserting {count} applicant profiles {encryption_status}...")
            
            query = """
            INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for i in range(count):
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                birth_date = self.generate_birth_date()
                address = self.generate_address()
                phone = self.generate_phone_number()
                
                if use_encryption:
                    first_name = self.encrypt_data(first_name)
                    last_name = self.encrypt_data(last_name)
                    birth_date_encrypted = self.encrypt_data(str(birth_date))
                    address = self.encrypt_data(address)
                    phone = self.encrypt_data(phone)
                    
                    applicant_data = (first_name, last_name, birth_date_encrypted, address, phone)
                else:
                    applicant_data = (first_name, last_name, birth_date, address, phone)
                cursor.execute(query, applicant_data)
                
                if (i + 1) % 50 == 0:
                    self.connection.commit()
                    print(f"[*] Inserted {i + 1}/{count} profiles...")
            
            self.connection.commit()
            cursor.close()
            print(f"[+] Successfully seeded {count} applicant profiles {encryption_status}")
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
                    role = self.generate_job_role()
                    
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

    def verify_seeded_data(self, show_decrypted: bool = False) -> None:
        try:
            if not self.connection:
                return
                
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as total FROM ApplicantProfile")
            profile_count = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM ApplicationDetail") 
            detail_count = cursor.fetchone()['total']

            cursor.execute("SELECT * FROM ApplicantProfile LIMIT 5")
            sample_data = cursor.fetchall()
            cursor.close()
            
            print(f"\n[+] Database Statistics:")
            print(f"    Total ApplicantProfile records: {profile_count}")
            print(f"    Total ApplicationDetail records: {detail_count}")
            print(f"\n[+] Sample data (first 5 profiles):")
            
            for record in sample_data:
                if show_decrypted and self.encryption_key:
                    first_name = self.decrypt_data(record['first_name'])
                    last_name = self.decrypt_data(record['last_name'])
                    birth_date = self.decrypt_data(str(record['date_of_birth']))
                    address = self.decrypt_data(record['address'])
                    phone = self.decrypt_data(record['phone_number'])
                    print(f"    ID: {record['applicant_id']}, "
                          f"Name: {first_name} {last_name} (decrypted), "
                          f"DOB: {birth_date} (decrypted), "
                          f"Phone: {phone} (decrypted)")
                else:
                    display_phone = record['phone_number'][:15] + "..." if len(record['phone_number']) > 15 else record['phone_number']
                    is_encrypted = self._is_hex_string(record['first_name'])
                    encryption_status = "(encrypted)" if is_encrypted else "(plain text)"
                    print(f"    ID: {record['applicant_id']}, "
                          f"Name: {record['first_name'][:20]}... {encryption_status}, "
                          f"DOB: {str(record['date_of_birth'])[:20]}..., "
                          f"Phone: {display_phone}")
                      
        except Error as e:
            print(f"[-] Error verifying data: {e}")

def main() -> None:
    print("Database Seeder for ATS System")
    print("=" * 40)
    
    try:
        seeder = DatabaseSeeder()
        
        if not seeder.connect():
            print("[-] Failed to connect to database")
            return
        
        print("\nSelect seeding option:")
        print("1. Generate new data (ApplicantProfile + ApplicationDetail)")
        print("2. Generate ApplicantProfile only")
        print("3. Generate ApplicationDetail only")
        print("4. Import from SQL file (tubes3_seeding.sql)")
        print("5. Clear all data")
        print("6. Show database statistics")
        print("7. Encrypt existing database data")
        print("8. Decrypt existing database data")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            use_encryption = False
            if encrypt is not None and seeder.encryption_key is not None:
                encryption_choice = input("Use encryption for sensitive data? (Y/n): ").lower().strip()
                if encryption_choice != 'n':
                    use_encryption = True
                    print("[*] Using encryption key from configuration")
            elif encrypt is not None:
                encryption_choice = input("Use encryption for sensitive data? (y/N): ").lower().strip()
                if encryption_choice == 'y':
                    key_input = input("Enter encryption key: ").strip()
                    if key_input and seeder.set_encryption_key(key_input):
                        use_encryption = True
            
            clear_data = input("Clear all existing data first? (y/N): ").lower().strip()
            if clear_data == 'y':
                seeder.clear_existing_data()
            
            try:
                count_input = input("Enter number of applicant profiles to create (default: 200): ").strip()
                count = int(count_input) if count_input else 200
                if count <= 0:
                    count = 200
            except ValueError:
                count = 200
            
            if seeder.seed_applicant_profiles(count, use_encryption):
                if seeder.seed_application_details():
                    show_decrypted = False
                    if use_encryption and seeder.encryption_key:
                        decrypt_choice = input("Show decrypted data in verification? (y/N): ").lower().strip()
                        show_decrypted = decrypt_choice == 'y'
                    
                    seeder.verify_seeded_data(show_decrypted)
                    print(f"\n[+] Complete seeding process finished successfully!")
                    
        elif choice == '2':
            use_encryption = False
            if encrypt is not None and seeder.encryption_key is not None:
                encryption_choice = input("Use encryption for sensitive data? (Y/n): ").lower().strip()
                if encryption_choice != 'n':
                    use_encryption = True
                    print("[*] Using encryption key from configuration")
            elif encrypt is not None:
                encryption_choice = input("Use encryption for sensitive data? (y/N): ").lower().strip()
                if encryption_choice == 'y':
                    key_input = input("Enter encryption key: ").strip()
                    if key_input and seeder.set_encryption_key(key_input):
                        use_encryption = True
            
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
            
            if seeder.seed_applicant_profiles(count, use_encryption):
                show_decrypted = False
                if use_encryption and seeder.encryption_key:
                    decrypt_choice = input("Show decrypted data in verification? (y/N): ").lower().strip()
                    show_decrypted = decrypt_choice == 'y'
                
                seeder.verify_seeded_data(show_decrypted)
                print(f"\n[+] Applicant seeding completed successfully!")
                
        elif choice == '3':
            clear_data = input("Clear existing ApplicationDetail data? (y/N): ").lower().strip()
            if clear_data == 'y':
                seeder.clear_existing_application_data()
            
            if seeder.seed_application_details():
                seeder.verify_seeded_data()
                print(f"\n[+] Application detail seeding completed successfully!")
                
        elif choice == '4':
            sql_file_path = os.path.join(current_dir, '..', 'src', 'db', 'tubes3_seeding.sql')
            sql_file_path = os.path.normpath(sql_file_path)
            
            print(f"[*] Using SQL file: {sql_file_path}")
            
            clear_data = input("Clear all existing data first? (y/N): ").lower().strip()
            if clear_data == 'y':
                seeder.clear_existing_data()
            
            if seeder.execute_sql_file(sql_file_path):
                seeder.verify_seeded_data()
                print(f"\n[+] SQL file import completed successfully!")
            else:
                print(f"\n[-] SQL file import failed!")
                
        elif choice == '5':
            confirm = input("Are you sure you want to clear ALL data? (y/N): ").lower().strip()
            if confirm == 'y':
                if seeder.clear_existing_data():
                    print("[+] All data cleared successfully!")
                    
        elif choice == '6':
            seeder.verify_seeded_data()
            
        elif choice == '7':
            if encrypt is None:
                print("[-] Encryption module not available")
                return

            if seeder.encryption_key is None:
                print("[-] No encryption key available from configuration")
                key_input = input("Enter encryption key manually: ").strip()
                if not key_input:
                    print("[-] Encryption key is required")
                    return
                if not seeder.set_encryption_key(key_input):
                    return
            else:
                print("[*] Using encryption key from configuration")
            
            print("\n[!] WARNING: This will encrypt all existing plain text data in the database!")
            print("    Make sure you have a backup before proceeding.")
            
            backup_choice = input("Create backup before encryption? (Y/n): ").lower().strip()
            if backup_choice != 'n':
                print("[*] Creating backup...")
                seeder.backup_database()
            
            confirm = input("Proceed with encryption? (y/N): ").lower().strip()
            if confirm == 'y':
                if seeder.encrypt_existing_data():
                    print("\n[+] Database encryption completed!")
                    print("    Use option 6 to verify the results")
                else:
                    print("\n[-] Database encryption failed!")
            else:
                print("[-] Encryption cancelled")
                
        elif choice == '8':
            if encrypt is None:
                print("[-] Encryption module not available")
                return
            
            if seeder.encryption_key is None:
                print("[-] No encryption key available from configuration")
                key_input = input("Enter decryption key manually: ").strip()
                if not key_input:
                    print("[-] Decryption key is required")
                    return
                if not seeder.set_encryption_key(key_input):
                    return
            else:
                print("[*] Using encryption key from configuration")
            
            print("\n[!] WARNING: This will decrypt all existing encrypted data in the database!")
            print("    Make sure you have the correct key and a backup before proceeding.")
            
            backup_choice = input("Create backup before decryption? (Y/n): ").lower().strip()
            if backup_choice != 'n':
                print("[*] Creating backup...")
                seeder.backup_database()
            
            confirm = input("Proceed with decryption? (y/N): ").lower().strip()
            if confirm == 'y':
                if seeder.decrypt_existing_data():
                    print("\n[+] Database decryption completed!")
                    print("    Use option 6 to verify the results")
                else:
                    print("\n[-] Database decryption failed!")
            else:
                print("[-] Decryption cancelled")
        
        elif choice == '9':
            print("[*] Exiting seeder script")
            return
            
        else:
            print("Invalid choice. Please select 1-8.")
        
    except KeyboardInterrupt:
        print("\n[-] Process interrupted by user")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
    finally:
        try:
            seeder.disconnect()
        except:
            pass

if __name__ == "__main__":
    main()