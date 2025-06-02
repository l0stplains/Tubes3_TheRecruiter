#!/usr/bin/env python3
"""
Test script untuk insert data ke database ATS
Location: src/db/test_insert.py
Run: cd src/db && python test_insert.py
"""

import sys
import os
from datetime import date

# Add parent directory to path untuk import utils
sys.path.append('../')

from models import DatabaseManager
from utils.config import DatabaseConfig

def test_insert_data():
    """Test insert data ke database"""
    
    print("=== Testing Database Insert ===")
    
    # Test dengan hardcode credentials (tidak perlu .env)
    print("\n1. Testing direct connection...")
    db_manager = DatabaseManager(
        host='localhost',
        database='ats_system',
        user='gongyoo',
        password='roulette',
        port=2025
    )
    
    if not db_manager.initialize():
        print("❌ Database connection failed!")
        print("💡 Make sure docker-compose is running: docker-compose up -d")
        return False
    
    print("✅ Database connected successfully!")
    
    # Test data sesuai contoh di spesifikasi (Gambar 4 & 5)
    test_applicants = [
        {
            'first_name': 'Farhan',
            'last_name': '',
            'date_of_birth': '1999-10-05',
            'address': 'Masjid Salman ITB',
            'phone_number': '0812 3456 7890'
        },
        {
            'first_name': 'Aland',
            'last_name': '',
            'date_of_birth': '1998-05-15',
            'address': 'Ganesha, Bandung',
            'phone_number': '0813 4567 8901'
        },
        {
            'first_name': 'Ariel',
            'last_name': '',
            'date_of_birth': '1997-08-22',
            'address': 'Dago, Bandung',
            'phone_number': '0814 5678 9012'
        }
    ]
    
    print("\n2. Inserting test applicants...")
    
    for i, applicant_data in enumerate(test_applicants, 1):
        print(f"\n   Inserting applicant {i}: {applicant_data['first_name']}")
        
        # Insert applicant
        applicant_id = db_manager.applicant_profile.insert(applicant_data)
        
        if applicant_id:
            print(f"   ✅ Applicant inserted with ID: {applicant_id}")
            
            # Insert sample applications untuk setiap applicant
            applications = [
                {
                    'applicant_id': applicant_id,
                    'application_role': 'Software Engineer',
                    'cv_path': f'data/{applicant_data["first_name"].lower()}_software_engineer.pdf'
                },
                {
                    'applicant_id': applicant_id,
                    'application_role': 'Backend Developer',
                    'cv_path': f'data/{applicant_data["first_name"].lower()}_backend_dev.pdf'
                }
            ]
            
            for app_data in applications:
                app_id = db_manager.application_detail.insert(app_data)
                if app_id:
                    print(f"   ✅ Application inserted with ID: {app_id} ({app_data['application_role']})")
                else:
                    print(f"   ❌ Failed to insert application: {app_data['application_role']}")
        else:
            print(f"   ❌ Failed to insert applicant: {applicant_data['first_name']}")
    
    print("\n3. Querying inserted data...")
    
    # Test query all data
    all_applications = db_manager.application_detail.get_all_with_profiles()
    
    print(f"\n📊 Total applications in database: {len(all_applications)}")
    print("\n   Applications list:")
    
    for app in all_applications:
        full_name = f"{app['first_name']} {app['last_name']}".strip()
        print(f"   - ID: {app['detail_id']} | {full_name} | {app['application_role']} | {app['cv_path']}")
    
    # Test query specific data
    print("\n4. Testing specific queries...")
    
    # Get specific applicant
    if len(all_applications) > 0:
        first_app = all_applications[0]
        applicant = db_manager.applicant_profile.get_by_id(first_app['applicant_id'])
        if applicant:
            print(f"   ✅ Applicant ID {first_app['applicant_id']}: {applicant['first_name']} {applicant['last_name']}")
        
        # Get specific application
        application = db_manager.application_detail.get_by_id(first_app['detail_id'])
        if application:
            print(f"   ✅ Application ID {first_app['detail_id']}: {application['first_name']} - {application['application_role']}")
    
    print("\n5. Testing data for pattern matching...")
    
    # Simulate data yang akan digunakan untuk pattern matching KMP/BM
    print("\n   Data ready for pattern matching:")
    for app in all_applications[:3]:  # Show first 3
        cv_path = app['cv_path']
        applicant_name = f"{app['first_name']} {app['last_name']}".strip()
        print(f"   - CV: {cv_path}")
        print(f"     Applicant: {applicant_name}")
        print(f"     Role: {app['application_role']}")
        print(f"     Phone: {app['phone_number']}")
        print()
    
    db_manager.close()
    print("✅ Database test completed successfully!")
    return True

def test_with_config():
    """Test menggunakan config.py"""
    
    print("\n=== Testing with DatabaseConfig ===")
    
    try:
        config = DatabaseConfig()
        db_manager = DatabaseManager(**config.get_connection_params())
        
        if db_manager.initialize():
            print("✅ Database connected using DatabaseConfig!")
            
            # Quick test
            all_apps = db_manager.application_detail.get_all_with_profiles()
            print(f"📊 Found {len(all_apps)} applications in database")
            
            db_manager.close()
            return True
        else:
            print("❌ Failed to connect using DatabaseConfig!")
            return False
            
    except Exception as e:
        print(f"❌ Error with DatabaseConfig: {e}")
        return False

def clear_test_data():
    """Clear all test data from database"""
    
    print("\n=== Clearing Test Data ===")
    
    db_manager = DatabaseManager(
        host='localhost',
        database='ats_system',
        user='gongyoo',
        password='roulette',
        port=2025
    )
    
    if db_manager.initialize():
        # Delete all data (ApplicationDetail first karena foreign key)
        db_manager.db_connection.execute_query("DELETE FROM ApplicationDetail")
        db_manager.db_connection.execute_query("DELETE FROM ApplicantProfile")
        
        # Reset auto increment
        db_manager.db_connection.execute_query("ALTER TABLE ApplicationDetail AUTO_INCREMENT = 1")
        db_manager.db_connection.execute_query("ALTER TABLE ApplicantProfile AUTO_INCREMENT = 1")
        
        print("✅ All test data cleared!")
        db_manager.close()
        return True
    else:
        print("❌ Failed to connect for data clearing!")
        return False

if __name__ == "__main__":
    print("🚀 Starting ATS Database Test")
    print("📍 Location: src/db/test_insert.py\n")
    
    # Ask user what to do
    print("Choose an option:")
    print("1. Insert test data")
    print("2. Clear all data")
    print("3. Both (clear then insert)")
    
    choice = input("\nEnter choice (1-3, default=1): ").strip() or "1"
    
    success = False
    
    if choice == "1":
        # Test 1: Insert data
        success = test_insert_data()
        # Test 2: Config test
        config_success = test_with_config()
        success = success and config_success
        
    elif choice == "2":
        # Clear data only
        success = clear_test_data()
        
    elif choice == "3":
        # Clear then insert
        clear_success = clear_test_data()
        if clear_success:
            success = test_insert_data()
            config_success = test_with_config()
            success = success and config_success
    
    print(f"\n{'='*50}")
    print("📋 Test Summary:")
    print(f"   Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 Database is ready for ATS system!")
        print("\n💡 Next steps:")
        print("   1. Implement pattern matching algorithms (KMP, Boyer-Moore)")
        print("   2. Create PDF extraction for CV files")
        print("   3. Build GUI interface with PyQt5")
        print("   4. Add fuzzy matching with Levenshtein Distance")
    else:
        print("\n⚠️  Some tests failed. Check your database configuration.")
        print("   - Make sure Docker is running: docker-compose up -d")
        print("   - Check if port 2025 is available")
        print("   - Verify database credentials")
    
    print(f"\n📊 You can check the data at: http://localhost:8080")
    print(f"   Login: gongyoo / roulette")