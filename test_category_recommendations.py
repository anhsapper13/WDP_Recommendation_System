#!/usr/bin/env python3

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.database import get_db
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_category_enhanced_recommendations():
    """Test collaborative filtering recommendations with survey category enhancement"""
    try:
        # Get database session
        db = next(get_db())
        
        # Initialize recommendation system
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Test with a user ID that should exist
        user_id = "7d38c0bc-451b-4c18-b899-c9ce6e320baa"
        
        print(f"🧪 Testing category-enhanced collaborative recommendations for user: {user_id}")
        print("=" * 80)
        
        # First, let's check the survey data to see what categories exist
        print("📊 SURVEY DATA ANALYSIS:")
        user_surveys = recommender.get_user_survey_data()
        print(f"Total survey records: {len(user_surveys)}")
        print(f"Unique users: {user_surveys['user_id'].nunique()}")
        print(f"Unique risk levels: {user_surveys['risk_level'].unique()}")
        print(f"Unique categories: {user_surveys['category_id'].unique()}")
        
        # Check current user's profile
        current_user_data = user_surveys[user_surveys['user_id'] == user_id]
        if not current_user_data.empty:
            user_info = current_user_data.iloc[0]
            print(f"\n👤 CURRENT USER PROFILE:")
            print(f"   Risk level: {user_info['risk_level']}")
            print(f"   Survey category: {user_info['category_id']}")
            
            # Find users with same risk and category
            same_risk_and_category = user_surveys[
                (user_surveys['risk_level'] == user_info['risk_level']) &
                (user_surveys['category_id'] == user_info['category_id']) &
                (user_surveys['user_id'] != user_id)
            ]
            print(f"   Users with same risk+category: {len(same_risk_and_category)}")
            if len(same_risk_and_category) > 0:
                print(f"   Similar users: {list(same_risk_and_category['user_id'].unique())}")
        
        print("\n" + "=" * 80)
        
        # Test collaborative filtering with category enhancement
        result = recommender.collaborative_filtering_recommendations(user_id, top_k=5)
        
        print(f"\n✅ Category-enhanced collaborative filtering completed!")
        print(f"📚 Courses found: {len(result.get('courses', []))}")
        print(f"👩‍⚕️ Consultants found: {len(result.get('consultants', []))}")
        
        # Show detailed course recommendations
        courses = result.get('courses', [])
        if courses:
            print(f"\n📚 COURSE RECOMMENDATIONS:")
            for i, course in enumerate(courses, 1):
                print(f"   {i}. {course.get('title', 'N/A')}")
                print(f"      ID: {course.get('course_id')}")
                print(f"      Score: {course.get('similarity_score', 0):.3f}")
                print(f"      Source User: {course.get('source_user', 'N/A')}")
                print()
        
        # Show detailed consultant recommendations
        consultants = result.get('consultants', [])
        if consultants:
            print(f"👩‍⚕️ CONSULTANT RECOMMENDATIONS:")
            for i, consultant in enumerate(consultants, 1):
                print(f"   {i}. {consultant.get('name', 'N/A')}")
                print(f"      ID: {consultant.get('consultant_id')}")
                print(f"      Score: {consultant.get('similarity_score', 0):.3f}")
                print(f"      Reason: {consultant.get('reason', 'N/A')}")
                print(f"      Source User: {consultant.get('source_user', 'N/A')}")
                print()
        
        # Test JSON serialization
        import json
        json_str = json.dumps(result, default=str)
        print(f"✅ JSON serialization test passed! Length: {len(json_str)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_category_enhanced_recommendations()
    exit(0 if success else 1)
