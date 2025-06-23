#!/usr/bin/env python3
"""
Database Connection Test Script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database.database import engine, SessionLocal
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_basic_connection():
    """Test basic database connection"""
    print("🔌 Testing basic database connection...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"✅ Database connected successfully!")
            print(f"📊 PostgreSQL Version: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_session_connection():
    """Test SQLAlchemy session"""
    print("\n🔄 Testing SQLAlchemy session...")
    try:
        db = SessionLocal()
        # Test simple query
        result = db.execute(text("SELECT current_database(), current_user"))
        row = result.fetchone()
        print(f"✅ Session connected successfully!")
        print(f"📊 Current Database: {row[0]}")
        print(f"👤 Current User: {row[1]}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Session connection failed: {str(e)}")
        return False

def test_tables_exist():
    """Test if required tables exist"""
    print("\n📋 Checking if required tables exist...")
    
    required_tables = [
        'users',
        'survey_attempts', 
        'courses',
        'consultants',
        'appointments',
        'course_enrollments',
        'risk_assessment_rules'
    ]
    
    try:
        db = SessionLocal()
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table} LIMIT 1"))
                count = result.fetchone()[0]
                existing_tables.append(f"{table} ({count} records)")
                print(f"✅ Table '{table}' exists with {count} records")
            except Exception as e:
                missing_tables.append(table)
                print(f"❌ Table '{table}' missing or inaccessible: {str(e)}")
        
        db.close()
        
        print(f"\n📊 Summary:")
        print(f"✅ Existing tables: {len(existing_tables)}")
        print(f"❌ Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print(f"🔧 Missing tables: {', '.join(missing_tables)}")
            return False
        else:
            print("🎉 All required tables exist!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return False

def test_recommendation_system():
    """Test the recommendation system data access"""
    print("\n🤖 Testing recommendation system data access...")
    
    try:
        db = SessionLocal()
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Test get_user_survey_data
        print("📊 Testing get_user_survey_data()...")
        survey_df = recommender.get_user_survey_data()
        print(f"✅ Survey data: {len(survey_df)} records, columns: {list(survey_df.columns) if not survey_df.empty else 'No data'}")
        
        # Test get_courses_data
        print("📚 Testing get_courses_data()...")
        courses_df = recommender.get_courses_data()
        print(f"✅ Courses data: {len(courses_df)} records, columns: {list(courses_df.columns) if not courses_df.empty else 'No data'}")
        
        # Test get_consultants_data
        print("👨‍⚕️ Testing get_consultants_data()...")
        consultants_df = recommender.get_consultants_data()
        print(f"✅ Consultants data: {len(consultants_df)} records, columns: {list(consultants_df.columns) if not consultants_df.empty else 'No data'}")
        
        # Test get_user_interactions
        print("🔄 Testing get_user_interactions()...")
        interactions_df = recommender.get_user_interactions()
        print(f"✅ Interactions data: {len(interactions_df)} records, columns: {list(interactions_df.columns) if not interactions_df.empty else 'No data'}")
        
        db.close()
        
        total_records = len(survey_df) + len(courses_df) + len(consultants_df) + len(interactions_df)
        print(f"\n🎯 Total records across all tables: {total_records}")
        
        if total_records > 0:
            print("✅ Recommendation system can access data successfully!")
            return True
        else:
            print("⚠️  No data found in tables - database might be empty")
            return False
            
    except Exception as e:
        print(f"❌ Recommendation system test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Database Connection & Recommendation System Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Basic connection
    if test_basic_connection():
        tests_passed += 1
    
    # Test 2: Session connection
    if test_session_connection():
        tests_passed += 1
    
    # Test 3: Tables exist
    if test_tables_exist():
        tests_passed += 1
    
    # Test 4: Recommendation system
    if test_recommendation_system():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Database is ready for use.")
    elif tests_passed >= 2:
        print("⚠️  Database connected but some issues found. Check the logs above.")
    else:
        print("❌ Major database issues found. Please fix configuration.")
    
    print("\n💡 Next steps:")
    if tests_passed < 2:
        print("1. Check PostgreSQL is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure database 'drug_prevention' exists")
    elif tests_passed < 3:
        print("1. Run database migrations to create tables")
        print("2. Insert sample data for testing")
    else:
        print("1. Database is ready!")
        print("2. You can now test the API endpoints")

if __name__ == "__main__":
    main()
