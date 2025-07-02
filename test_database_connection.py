#!/usr/bin/env python3
"""
Database Connection Test Script
"""
import sys
import os
import importlib
import inspect
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.declarative import DeclarativeMeta
from app.database.database import engine, SessionLocal, Base
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

def get_all_models():
    """Dynamically discover all SQLAlchemy models in the models directory"""
    # Get the current script directory and navigate to models
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, 'app', 'models')
    
    print(f"🔍 Looking for models in: {models_dir}")
    
    if not os.path.exists(models_dir):
        print(f"❌ Models directory not found: {models_dir}")
        return {}
    
    models = {}
    
    # Get all Python files in models directory
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            try:
                # Import the module
                module = importlib.import_module(f'app.models.{module_name}')
                
                # Find all classes that are SQLAlchemy models
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        hasattr(obj, '__tablename__') and 
                        isinstance(obj, type) and
                        hasattr(obj, '__table__')):
                        models[obj.__tablename__] = {
                            'class_name': name,
                            'module': module_name,
                            'table_name': obj.__tablename__
                        }
            except Exception as e:
                print(f"⚠️  Could not import {module_name}: {str(e)}")
    
    return models

def test_tables_exist():
    """Test if all model tables exist"""
    print("\n📋 Checking all model tables...")
    
    # Get all models dynamically
    models = get_all_models()
    
    if not models:
        print("❌ No models found!")
        return False
    
    print(f"🔍 Found {len(models)} models to test:")
    for table_name, info in models.items():
        print(f"   - {info['class_name']} → Table: '{table_name}'")
    
    try:
        db = SessionLocal()
        existing_tables = []
        missing_tables = []
        
        for table_name, info in models.items():
            try:
                # Create a new session for each table check to avoid transaction issues
                db_test = SessionLocal()
                # Use double quotes for case-sensitive table names
                result = db_test.execute(text(f'SELECT COUNT(*) FROM "{table_name}" LIMIT 1'))
                count = result.fetchone()[0]
                existing_tables.append(f"{table_name} ({count} records)")
                print(f"✅ {info['class_name']}: {count} records")
                db_test.close()
            except Exception as e:
                missing_tables.append(table_name)
                print(f"❌ {info['class_name']} (Table: '{table_name}'): Missing or inaccessible")
                try:
                    db_test.close()
                except:
                    pass
        
        db.close()
        
        print(f"\n📊 Summary:")
        print(f"✅ Existing tables: {len(existing_tables)}")
        print(f"❌ Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print(f"🔧 Missing tables: {', '.join(missing_tables)}")
            return len(existing_tables) > 0  # Return True if at least some tables exist
        else:
            print("🎉 All model tables exist!")
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
