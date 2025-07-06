#!/usr/bin/env python3
"""
Test script to verify fallback scenario when no users with same risk+category are available
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.service.recommendation_action import RecommendationService

async def test_fallback_scenario():
    """Test fallback when no users have same risk+category but same risk exists"""
    
    print("🧪 Testing fallback scenario for collaborative recommendations")
    print("=" * 80)
    
    service = RecommendationService()
    
    # Test với user có risk level khác để thử fallback
    # Trước tiên, xem có user nào trong data có risk level khác không
    user_surveys = service.get_user_survey_data()
    print(f"📊 AVAILABLE SURVEY DATA:")
    print(f"Total survey records: {len(user_surveys)}")
    print(f"Unique users: {user_surveys['user_id'].nunique()}")
    print(f"Risk level distribution: {user_surveys['risk_level'].value_counts().to_dict()}")
    print(f"Category distribution: {user_surveys['category_id'].value_counts().to_dict()}")
    
    # Tìm user có risk level khác để test
    risk_levels = user_surveys['risk_level'].unique()
    print(f"\nAvailable risk levels: {risk_levels}")
    
    for risk_level in risk_levels:
        users_with_risk = user_surveys[user_surveys['risk_level'] == risk_level]['user_id'].unique()
        print(f"\nUsers with risk level '{risk_level}': {len(users_with_risk)}")
        for user_id in users_with_risk[:2]:  # Show first 2 users
            user_data = user_surveys[user_surveys['user_id'] == user_id].iloc[0]
            print(f"  - {user_id}: category={user_data['category_id']}")
    
    # Test với một user có ít user cùng category
    # Chọn user có category hiếm hơn
    category_counts = user_surveys['category_id'].value_counts()
    print(f"\nCategory distribution: {category_counts.to_dict()}")
    
    # Lấy category có ít user nhất
    rare_category = category_counts.index[-1]  # Category có ít user nhất
    common_category = category_counts.index[0]  # Category có nhiều user nhất
    
    print(f"\nRare category: {rare_category} ({category_counts[rare_category]} users)")
    print(f"Common category: {common_category} ({category_counts[common_category]} users)")
    
    # Tìm user có rare category để test
    users_with_rare_category = user_surveys[user_surveys['category_id'] == rare_category]['user_id'].unique()
    
    if len(users_with_rare_category) > 0:
        test_user = users_with_rare_category[0]
        user_info = user_surveys[user_surveys['user_id'] == test_user].iloc[0]
        
        print(f"\n🎯 TESTING WITH USER: {test_user}")
        print(f"   Risk level: {user_info['risk_level']}")
        print(f"   Category: {user_info['category_id']}")
        
        # Count users with same risk+category
        same_risk_category = user_surveys[
            (user_surveys['risk_level'] == user_info['risk_level']) &
            (user_surveys['category_id'] == user_info['category_id']) &
            (user_surveys['user_id'] != test_user)
        ]
        
        # Count users with same risk only
        same_risk_only = user_surveys[
            (user_surveys['risk_level'] == user_info['risk_level']) &
            (user_surveys['user_id'] != test_user)
        ]
        
        print(f"   Users with same risk+category: {len(same_risk_category)}")
        print(f"   Users with same risk only: {len(same_risk_only)}")
        
        # Test collaborative filtering
        print(f"\n🤝 Testing collaborative filtering...")
        try:
            course_recommendations = service.collaborative_filtering_course_recommendations(test_user, top_k=5)
            consultant_recommendations = service.collaborative_filtering_consultant_recommendations(test_user, top_k=3)
            
            print(f"\n✅ RESULTS:")
            print(f"📚 Course recommendations: {len(course_recommendations)}")
            print(f"👩‍⚕️ Consultant recommendations: {len(consultant_recommendations)}")
            
            if course_recommendations:
                print(f"\n📚 COURSE RECOMMENDATIONS:")
                for i, rec in enumerate(course_recommendations, 1):
                    print(f"   {i}. {rec['title'][:40]}... (Score: {rec['similarity_score']:.4f})")
            
            if consultant_recommendations:
                print(f"\n👩‍⚕️ CONSULTANT RECOMMENDATIONS:")
                for i, rec in enumerate(consultant_recommendations, 1):
                    print(f"   {i}. {rec['name']} (Score: {rec['similarity_score']:.4f})")
                    
        except Exception as e:
            print(f"❌ Error during testing: {str(e)}")
    else:
        print(f"❌ No users found with rare category for testing")

if __name__ == "__main__":
    asyncio.run(test_fallback_scenario())
