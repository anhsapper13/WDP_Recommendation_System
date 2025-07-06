#!/usr/bin/env python3
"""
Test script to verify that get_user_risk_summary logs the user's survey category
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.database import get_db
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem

def test_user_category_logging():
    """Test that user survey categories are logged correctly"""
    print("=" * 60)
    print("🧪 Testing User Survey Category Logging")
    print("=" * 60)
    
    # Get database session
    db = next(get_db())
    service = CRAFFTASSISTRecommendationSystem(db)
    
    # Get some user IDs from the survey data
    try:
        survey_data = service.get_user_survey_data()
        if survey_data.empty:
            print("❌ No survey data found")
            return
        
        # Get unique user IDs
        user_ids = survey_data['user_id'].unique()[:5]  # Test first 5 users
        
        print(f"📊 Testing category logging for {len(user_ids)} users:")
        print()
        
        for user_id in user_ids:
            print(f"Testing user: {user_id}")
            
            # This should trigger the log message
            risk_summary = service.get_user_risk_summary(str(user_id))
            
            print(f"  ➡️  Risk Level: {risk_summary['latest_risk_level']}")
            print(f"  ➡️  Category ID: {risk_summary['latest_category_id']}")
            print(f"  ➡️  Total Surveys: {risk_summary['total_surveys_taken']}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_category_logging()
