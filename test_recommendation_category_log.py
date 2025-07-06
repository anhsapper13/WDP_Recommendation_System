#!/usr/bin/env python3
"""
Test script to verify category logging during recommendation flow
"""

import sys
import os

# Add the app directory to the Python path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.database import get_db
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_recommendation_with_category_logging():
    """Test that category logging works during recommendation flow"""
    print("=" * 80)
    print("🧪 Testing Category Logging During Recommendation Flow")
    print("=" * 80)
    
    try:
        # Get database session
        db = next(get_db())
        service = CRAFFTASSISTRecommendationSystem(db)
        
        # Use a known user ID
        user_id = "7d38c0bc-451b-4c18-b899-c9ce6e320baa"
        
        print(f"📊 Testing recommendations for user: {user_id}")
        print()
        
        # Test hybrid recommendations (should trigger category logging) 
        print("� Getting Hybrid Recommendations:")
        print("-" * 50)
        recommendations = service.hybrid_recommendations(user_id, top_k=5)
        
        print(f"  ➡️  Found {len(recommendations.get('courses', []))} course recommendations")
        print(f"  ➡️  Found {len(recommendations.get('consultants', []))} consultant recommendations")
        print()
        
        # Verify risk summary directly
        print("📋 Getting Risk Summary:")
        print("-" * 50)
        risk_summary = service.get_user_risk_summary(user_id)
        print(f"  ➡️  User Category: {risk_summary['latest_category_id']}")
        print(f"  ➡️  Risk Level: {risk_summary['latest_risk_level']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendation_with_category_logging()
