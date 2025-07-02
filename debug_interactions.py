#!/usr/bin/env python3
"""
Debug get_user_interactions function
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.database.database import SessionLocal
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def debug_user_interactions():
    """Debug user interactions function"""
    print("🔍 Debugging get_user_interactions function")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Get all interactions
        interactions_df = recommender.get_user_interactions()
        print(f"📊 Total interactions: {len(interactions_df)}")
        
        if not interactions_df.empty:
            print(f"\n📋 Columns: {list(interactions_df.columns)}")
            print(f"📊 Data types:\n{interactions_df.dtypes}")
            
            # Check unique user_ids
            print(f"\n👥 Unique user IDs:")
            unique_users = interactions_df['user_id'].unique()
            for i, user_id in enumerate(unique_users):
                if pd.isna(user_id):
                    print(f"   {i+1}. NULL/NaN")
                else:
                    print(f"   {i+1}. {user_id}")
            
            # Check for NULL values
            null_users = interactions_df['user_id'].isnull().sum()
            print(f"\n⚠️  Records with NULL user_id: {null_users}")
            
            # Filter valid user interactions
            valid_interactions = interactions_df[interactions_df['user_id'].notna()]
            print(f"✅ Valid interactions (non-NULL user_id): {len(valid_interactions)}")
            
            if not valid_interactions.empty:
                test_user_id = valid_interactions['user_id'].iloc[0]
                print(f"\n🧪 Testing with user_id: {test_user_id}")
                
                user_specific = valid_interactions[valid_interactions['user_id'] == test_user_id]
                print(f"   User-specific interactions: {len(user_specific)}")
                
                # Show sample data
                print(f"\n📝 Sample user interactions:")
                print(user_specific.head().to_string())
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_raw_sql_queries():
    """Test raw SQL queries to understand data"""
    print(f"\n🔍 Testing raw SQL queries")
    print("=" * 40)
    
    try:
        db = SessionLocal()
        
        # Test Course_Enrollment
        print("📚 Course_Enrollment data:")
        course_data = db.execute(db.text("""
            SELECT user_id, course_id, progress_percentage, enrollment_date
            FROM "Course_Enrollment"
            LIMIT 5
        """)).fetchall()
        
        print(f"   Records found: {len(course_data)}")
        for row in course_data:
            print(f"   User: {row.user_id}, Course: {row.course_id}, Progress: {row.progress_percentage}")
        
        # Test Appointments 
        print(f"\n📅 Appointments data:")
        appointment_data = db.execute(db.text("""
            SELECT "userId", "consultantId", status, booking_time
            FROM "Appointments"
            WHERE is_deleted = false
            LIMIT 5
        """)).fetchall()
        
        print(f"   Records found: {len(appointment_data)}")
        for row in appointment_data:
            print(f"   User: {row.userId}, Consultant: {row.consultantId}, Status: {row.status}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error in raw SQL: {str(e)}")

if __name__ == "__main__":
    debug_user_interactions()
    test_raw_sql_queries()
