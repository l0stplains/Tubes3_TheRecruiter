import sys
import os
from datetime import datetime, timedelta
import random
from typing import Optional, List, Tuple, Dict, Any

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

        self.first_names: List[str] = [
            'Andi', 'Budi', 'Citra', 'Dian', 'Eko', 'Fitri', 'Gina', 'Hadi', 'Indri', 'Joko',
            'Kartika', 'Linda', 'Maya', 'Nina', 'Oka', 'Putri', 'Rina', 'Sari', 'Toni', 'Uci',
            'Vina', 'Wati', 'Yani', 'Zara', 'Agus', 'Bayu', 'Cindy', 'Doni', 'Erni', 'Fajar',
            'Gita', 'Hana', 'Ivan', 'Juli', 'Kiki', 'Lala', 'Mira', 'Nita', 'Ocha', 'Popi',
            'Qori', 'Reza', 'Sita', 'Tari', 'Ulfa', 'Vera', 'Wina', 'Yudi', 'Zaki', 'Arif',
            'Bella', 'Cahya', 'Dewi', 'Elsa', 'Fani', 'Gani', 'Hesti', 'Ilham', 'Jeni', 'Kris',
            'Leni', 'Mila', 'Novi', 'Oki', 'Pira', 'Ratna', 'Sinta', 'Tika', 'Umi', 'Vika',
            'Widi', 'Yesi', 'Zahra', 'Ahmad', 'Bela', 'Cici', 'Dinda', 'Eva', 'Fadli', 'Galih',
            'Heru', 'Irma', 'Jihan', 'Karina', 'Laras', 'Monica', 'Nanda', 'Oscar', 'Pingkan',
            'Randi', 'Sofia', 'Tina', 'Ully', 'Vero', 'Wulan', 'Yusuf', 'Zidan', 'Arie', 'Bunga'
        ]
        
        self.last_names: List[str] = [
            'Wijaya', 'Santoso', 'Pratama', 'Susanto', 'Kurniawan', 'Sari', 'Putri', 'Handoko',
            'Lestari', 'Utomo', 'Wibowo', 'Hakim', 'Setiawan', 'Rahayu', 'Indah', 'Permana',
            'Anggraini', 'Nugroho', 'Maharani', 'Wardani', 'Suryani', 'Dewi', 'Purnama', 'Safitri',
            'Ramadhan', 'Sukma', 'Kusuma', 'Aditya', 'Cahaya', 'Melati', 'Pertiwi', 'Sartika',
            'Budiman', 'Atmaja', 'Kartini', 'Buana', 'Ananda', 'Saputra', 'Saputri', 'Manurung',
            'Sitompul', 'Panjaitan', 'Hasibuan', 'Simanjuntak', 'Lubis', 'Napitupulu', 'Siregar',
            'Johnson', 'Smith', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'
        ]
        
        self.addresses: List[str] = [
            'Jl. Merdeka No. 123, Jakarta',
            'Jl. Sudirman No. 456, Bandung',
            'Jl. Diponegoro No. 789, Surabaya',
            'Jl. Ahmad Yani No. 321, Medan',
            'Jl. Imam Bonjol No. 654, Semarang',
            'Jl. Gajah Mada No. 987, Yogyakarta',
            'Jl. Kartini No. 147, Malang',
            'Jl. Pemuda No. 258, Solo',
            'Jl. Veteran No. 369, Palembang',
            'Jl. Pahlawan No. 741, Makassar'
        ]

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
        prefixes = ['0812', '0813', '0821', '0822', '0823', '0851', '0852', '0853']
        prefix = random.choice(prefixes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}-{number[:4]}-{number[4:]}"

    def generate_birth_date(self) -> datetime:
        start_date = datetime(1980, 1, 1)
        end_date = datetime(2000, 12, 31)
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        return random_date.date()

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
            applicants: List[Tuple[str, str, datetime, str, str]] = []
            used_names = set()
            
            for i in range(count):
                while True:
                    first_name = random.choice(self.first_names)
                    last_name = random.choice(self.last_names)
                    full_name = f"{first_name} {last_name}"
                    
                    if full_name not in used_names:
                        used_names.add(full_name)
                        break
                
                applicant = (
                    first_name,
                    last_name,
                    self.generate_birth_date(),
                    random.choice(self.addresses),
                    self.generate_phone_number()
                )
                applicants.append(applicant)
            
            query = """
            INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.executemany(query, applicants)
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
    print("DATABASE SEEDER FOR ATS SYSTEM")
    print("="*50)
    
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