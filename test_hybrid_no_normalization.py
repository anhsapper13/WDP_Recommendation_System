#!/usr/bin/env python3
"""
Test script to verify hybrid recommendations work correctly with raw scores (no normalization)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_hybrid_recommendations():
    """Test hybrid recommendations with raw scores"""
    
    # Get database connection
    db = next(get_db())
    
    try:
        # Initialize recommendation system
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Test with a sample user (you may need to adjust this user_id based on your database)
        test_user_id = "1"  # Change this to an existing user ID in your database
        
        print(f"🧪 Testing hybrid recommendations for user: {test_user_id}")
        print("=" * 80)
        
        # Get hybrid recommendations
        results = recommender.hybrid_recommendations(test_user_id, top_k=5)
        
        print("\n🎯 HYBRID RECOMMENDATION RESULTS:")
        print("=" * 40)
        
        if results['status'] == 'success':
            print(f"✅ Success! Found recommendations:")
            print(f"   - Courses: {len(results['courses'])}")
            print(f"   - Consultants: {len(results['consultants'])}")
            
            # Show course recommendations with raw scores
            if results['courses']:
                print(f"\n📚 COURSE RECOMMENDATIONS:")
                for i, course in enumerate(results['courses'], 1):
                    score = course.get('hybrid_score', 0)
                    source = course.get('recommendation_source', 'unknown')
                    title = course.get('title', 'Unknown')[:50]
                    print(f"   {i}. {title}...")
                    print(f"      Raw Hybrid Score: {score:.4f}")
                    print(f"      Source: {source}")
                    print()
            
            # Show consultant recommendations with raw scores  
            if results['consultants']:
                print(f"👩‍⚕️ CONSULTANT RECOMMENDATIONS:")
                for i, consultant in enumerate(results['consultants'], 1):
                    score = consultant.get('hybrid_score', 0)
                    source = consultant.get('recommendation_source', 'unknown')
                    name = consultant.get('name', 'Unknown')
                    print(f"   {i}. {name}")
                    print(f"      Raw Hybrid Score: {score:.4f}")
                    print(f"      Source: {source}")
                    print()
            
            # Show configuration details
            config = results.get('hybrid_config', {})
            print(f"⚙️  HYBRID CONFIGURATION:")
            print(f"   Content Weight: {config.get('content_weight', 'N/A')}")
            print(f"   Collaborative Weight: {config.get('collaborative_weight', 'N/A')}")
            print(f"   Diversity Boost: {config.get('diversity_boost', 'N/A')}")
            print(f"   Normalization: DISABLED (using raw scores)")
            
        else:
            print(f"❌ Error: {results.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_hybrid_recommendations()
