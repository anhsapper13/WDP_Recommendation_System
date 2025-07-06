#!/usr/bin/env python3

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.database import get_db
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_collaborative_recommendations():
    """Test collaborative filtering recommendations to check UUID handling"""
    try:
        # Get database session
        db = next(get_db())
        
        # Initialize recommendation system
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Test with a user ID that should exist
        user_id = "7d38c0bc-451b-4c18-b899-c9ce6e320baa"
        
        print(f"🧪 Testing collaborative recommendations for user: {user_id}")
        print("=" * 60)
        
        # Test collaborative filtering
        result = recommender.collaborative_filtering_recommendations(user_id, top_k=5)
        
        print(f"✅ Collaborative filtering completed successfully!")
        print(f"📚 Courses found: {len(result.get('courses', []))}")
        print(f"👩‍⚕️ Consultants found: {len(result.get('consultants', []))}")
        
        # Show sample course recommendations
        courses = result.get('courses', [])
        if courses:
            print(f"\n📚 Sample Course Recommendations:")
            for i, course in enumerate(courses[:3], 1):
                print(f"   {i}. ID: {course.get('course_id')} (Type: {type(course.get('course_id'))})")
                print(f"      Title: {course.get('title', 'N/A')}")
                print(f"      Score: {course.get('similarity_score', 0):.3f}")
        
        # Show sample consultant recommendations
        consultants = result.get('consultants', [])
        if consultants:
            print(f"\n👩‍⚕️ Sample Consultant Recommendations:")
            for i, consultant in enumerate(consultants[:3], 1):
                print(f"   {i}. ID: {consultant.get('consultant_id')} (Type: {type(consultant.get('consultant_id'))})")
                print(f"      Name: {consultant.get('name', 'N/A')}")
                print(f"      Score: {consultant.get('similarity_score', 0):.3f}")
        
        # Test JSON serialization
        import json
        json_str = json.dumps(result, default=str)
        print(f"\n✅ JSON serialization test passed! Length: {len(json_str)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_collaborative_recommendations()
    exit(0 if success else 1)
