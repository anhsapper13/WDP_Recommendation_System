#!/usr/bin/env python3
"""
Test script for get_user_interactions function
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.database.database import SessionLocal
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_get_user_interactions():
    """Test the get_user_interactions function"""
    print("🧪 Testing get_user_interactions function")
    print("=" * 60)
    
    try:
        # Khởi tạo database session
        db = SessionLocal()
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        print("📊 Step 1: Calling get_user_interactions()...")
        interactions_df = recommender.get_user_interactions()
        
        print(f"✅ Function executed successfully!")
        print(f"📈 Data shape: {interactions_df.shape}")
        
        if interactions_df.empty:
            print("⚠️  No interaction data found in database")
            print("\n💡 This could mean:")
            print("   - Course_Enrollment table is empty")
            print("   - Appointments table is empty") 
            print("   - Database connection issues")
            
            # Test database tables individually
            print("\n🔍 Testing individual tables...")
            test_individual_tables(recommender)
            
        else:
            print(f"🎉 Found {len(interactions_df)} interaction records!")
            
            # Display data info
            print(f"\n📋 Columns: {list(interactions_df.columns)}")
            print(f"📊 Data types:\n{interactions_df.dtypes}")
            
            # Show item type distribution
            if 'item_type' in interactions_df.columns:
                print(f"\n📈 Item type distribution:")
                type_counts = interactions_df['item_type'].value_counts()
                for item_type, count in type_counts.items():
                    print(f"   {item_type}: {count} interactions")
            
            # Show rating distribution
            if 'rating' in interactions_df.columns:
                print(f"\n⭐ Rating statistics:")
                print(f"   Min rating: {interactions_df['rating'].min():.2f}")
                print(f"   Max rating: {interactions_df['rating'].max():.2f}")
                print(f"   Avg rating: {interactions_df['rating'].mean():.2f}")
            
            # Show unique users
            if 'user_id' in interactions_df.columns:
                unique_users = interactions_df['user_id'].nunique()
                print(f"\n👥 Unique users: {unique_users}")
            
            # Show sample data
            print(f"\n📝 Sample data (first 5 rows):")
            print(interactions_df.head().to_string())
            
            # Test with specific user
            if not interactions_df.empty:
                test_user_specific_interactions(interactions_df)
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error testing get_user_interactions: {str(e)}")
        return False
    
    return True

def test_individual_tables(recommender):
    """Test individual database tables"""
    try:
        # Test Course_Enrollment table
        print("\n📚 Testing Course_Enrollment table...")
        course_data = recommender.db.execute(recommender.db.text("""
            SELECT COUNT(*) as count FROM "Course_Enrollment"
        """)).fetchone()
        print(f"   Course enrollments: {course_data.count}")
        
        if course_data.count > 0:
            sample_data = recommender.db.execute(recommender.db.text("""
                SELECT user_id, course_id, progress_percentage, enrollment_date 
                FROM "Course_Enrollment" 
                LIMIT 3
            """)).fetchall()
            print("   Sample course enrollment data:")
            for row in sample_data:
                print(f"     User: {row.user_id}, Course: {row.course_id}, Progress: {row.progress_percentage}%")
        
        # Test Appointments table
        print("\n📅 Testing Appointments table...")
        appointment_data = recommender.db.execute(recommender.db.text("""
            SELECT COUNT(*) as count FROM "Appointments" WHERE is_deleted = false
        """)).fetchone()
        print(f"   Active appointments: {appointment_data.count}")
        
        if appointment_data.count > 0:
            sample_data = recommender.db.execute(recommender.db.text("""
                SELECT "userId", "consultantId", status, booking_time 
                FROM "Appointments" 
                WHERE is_deleted = false 
                LIMIT 3
            """)).fetchall()
            print("   Sample appointment data:")
            for row in sample_data:
                print(f"     User: {row.userId}, Consultant: {row.consultantId}, Status: {row.status}")
        
    except Exception as e:
        print(f"❌ Error testing individual tables: {str(e)}")

def test_user_specific_interactions(interactions_df):
    """Test interactions for specific users"""
    print(f"\n🔍 Testing user-specific interactions...")
    
    # Get a sample user ID
    sample_user_id = interactions_df['user_id'].iloc[0]
    print(f"📝 Testing with user ID: {sample_user_id}")
    
    # Filter interactions for this user
    user_interactions = interactions_df[interactions_df['user_id'] == sample_user_id]
    print(f"   User has {len(user_interactions)} interactions")
    
    # Show breakdown by item type
    if 'item_type' in user_interactions.columns:
        type_breakdown = user_interactions['item_type'].value_counts()
        for item_type, count in type_breakdown.items():
            print(f"   - {item_type}: {count} interactions")
    
    # Show user's interaction history
    print(f"   User's interaction details:")
    for _, interaction in user_interactions.iterrows():
        print(f"     {interaction['item_type']}: {interaction['item_id']} (rating: {interaction['rating']:.2f})")

def test_data_format():
    """Test if data format is correct for ML algorithms"""
    print(f"\n🤖 Testing data format for ML algorithms...")
    
    try:
        db = SessionLocal()
        recommender = CRAFFTASSISTRecommendationSystem(db)
        interactions_df = recommender.get_user_interactions()
        
        if interactions_df.empty:
            print("⚠️  No data to test ML format")
            return
        
        # Test pivot table creation (for collaborative filtering)
        print("📊 Testing pivot table creation...")
        
        # Test course interactions pivot
        course_interactions = interactions_df[interactions_df['item_type'] == 'course']
        if not course_interactions.empty:
            course_pivot = course_interactions.pivot_table(
                index='user_id',
                columns='item_id', 
                values='rating',
                fill_value=0
            )
            print(f"   ✅ Course pivot table: {course_pivot.shape}")
            print(f"      Users: {course_pivot.shape[0]}, Courses: {course_pivot.shape[1]}")
        
        # Test consultant interactions pivot  
        consultant_interactions = interactions_df[interactions_df['item_type'] == 'consultant']
        if not consultant_interactions.empty:
            consultant_pivot = consultant_interactions.pivot_table(
                index='user_id',
                columns='item_id',
                values='rating', 
                fill_value=0
            )
            print(f"   ✅ Consultant pivot table: {consultant_pivot.shape}")
            print(f"      Users: {consultant_pivot.shape[0]}, Consultants: {consultant_pivot.shape[1]}")
        
        print("✅ Data format is ready for ML algorithms!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error testing ML data format: {str(e)}")

def main():
    """Main test function"""
    print("🚀 get_user_interactions Function Test Suite")
    print("=" * 60)
    
    # Test 1: Basic function test
    success = test_get_user_interactions()
    
    if success:
        # Test 2: ML data format test
        test_data_format()
    
    print("\n" + "=" * 60)
    print("🎯 Test completed!")
    
    print("\n💡 Function Purpose:")
    print("   get_user_interactions() combines:")
    print("   1. Course enrollment data (user → course interactions)")
    print("   2. Appointment data (user → consultant interactions)")
    print("   3. Creates unified interaction matrix for collaborative filtering")
    
    print("\n📊 Expected Output:")
    print("   DataFrame with columns: user_id, item_id, item_type, rating, interaction_date")
    print("   - item_type: 'course' or 'consultant'")
    print("   - rating: 0.0-1.0 (progress % for courses, status for appointments)")

if __name__ == "__main__":
    main()
