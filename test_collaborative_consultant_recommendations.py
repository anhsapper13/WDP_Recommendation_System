#!/usr/bin/env python3
"""
Test script for collaborative_filtering_consultant_recommendations function
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database.database import SessionLocal
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
import json

def test_collaborative_consultant_recommendations():
    """Test collaborative filtering for consultant recommendations"""
    print("🤝 Testing Collaborative Filtering - Consultant Recommendations")
    print("=" * 70)
    
    try:
        # Khởi tạo database session và recommender
        db = SessionLocal()
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Bước 1: Lấy danh sách users có survey data
        print("👥 Step 1: Getting users with survey data...")
        user_surveys = recommender.get_user_survey_data()
        
        if user_surveys.empty:
            print("❌ No survey data found!")
            return
        
        print(f"✅ Found {len(user_surveys)} survey records")
        print(f"📊 Risk level distribution:")
        risk_distribution = user_surveys['risk_level'].value_counts()
        for risk, count in risk_distribution.items():
            print(f"   - {risk}: {count} users")
        
        # Bước 2: Lấy user interactions data
        print("\n🔄 Step 2: Getting user interactions...")
        interactions_df = recommender.get_user_interactions()
        
        if interactions_df.empty:
            print("❌ No interaction data found!")
            return
        
        print(f"✅ Found {len(interactions_df)} interactions")
        consultant_interactions = interactions_df[interactions_df['item_type'] == 'consultant']
        print(f"📅 Consultant appointments: {len(consultant_interactions)}")
        
        # Show interaction breakdown
        if not consultant_interactions.empty:
            print(f"📊 Consultant interaction breakdown:")
            rating_distribution = consultant_interactions['rating'].value_counts().sort_index()
            for rating, count in rating_distribution.items():
                status = "Completed" if rating >= 0.8 else "Confirmed" if rating >= 0.5 else "Pending"
                print(f"   - Rating {rating} ({status}): {count} appointments")
        
        # Bước 3: Test với 3 users có risk level khác nhau
        print("\n🎯 Step 3: Testing with different users...")
        
        # Lấy sample users từ mỗi risk level
        test_users = []
        for risk_level in ['HIGH', 'MEDIUM', 'LOW']:
            users_in_risk = user_surveys[user_surveys['risk_level'] == risk_level]['user_id'].unique()
            if len(users_in_risk) > 0:
                test_users.append({
                    'user_id': users_in_risk[0],
                    'risk_level': risk_level
                })
        
        if not test_users:
            print("❌ No test users found!")
            return
        
        print(f"👤 Testing with {len(test_users)} users:")
        for user in test_users:
            print(f"   - User {user['user_id']}: {user['risk_level']} risk")
        
        # Bước 4: Test collaborative filtering cho từng user
        for i, test_user in enumerate(test_users, 1):
            print(f"\n🔍 Test {i}: User {test_user['user_id']} ({test_user['risk_level']} risk)")
            print("-" * 50)
            
            # Gọi function collaborative_filtering_consultant_recommendations
            recommendations = recommender.collaborative_filtering_consultant_recommendations(
                user_id=test_user['user_id'],
                top_k=5
            )
            
            print(f"📊 Results for {test_user['user_id']}:")
            
            if not recommendations:
                print("   ❌ No recommendations generated")
                
                # Debug: Kiểm tra tại sao không có recommendations
                print("   🔍 Debug info:")
                
                # Check if user has survey data
                user_survey = user_surveys[user_surveys['user_id'] == test_user['user_id']]
                if user_survey.empty:
                    print("   - ❌ No survey data for this user")
                else:
                    print(f"   - ✅ Survey data: Risk={user_survey.iloc[0]['risk_level']}")
                
                # Check users with same risk level
                same_risk_users = user_surveys[
                    (user_surveys['risk_level'] == test_user['risk_level']) &
                    (user_surveys['user_id'] != test_user['user_id'])
                ]['user_id'].unique()
                print(f"   - 👥 Users with same risk level: {len(same_risk_users)}")
                
                # Check consultant interactions for same risk users
                if len(same_risk_users) > 0:
                    same_risk_interactions = consultant_interactions[
                        consultant_interactions['user_id'].isin(same_risk_users)
                    ]
                    print(f"   - 📅 Consultant interactions from similar users: {len(same_risk_interactions)}")
                
            else:
                print(f"   ✅ Generated {len(recommendations)} recommendations:")
                
                for j, rec in enumerate(recommendations, 1):
                    print(f"   {j}. {rec['name']}")
                    print(f"      - Specialization: {rec['specialization']}")
                    print(f"      - Experience: {rec['experience_years']} years")
                    print(f"      - Predicted Rating: {rec['predicted_rating']:.3f}")
                    print(f"      - Similarity Score: {rec['similarity_score']:.3f}")
                    print(f"      - Total Appointments: {rec['total_appointments']}")
                    print(f"      - Reason: {rec['reason']}")
                    print(f"      - Type: {rec['recommendation_type']}")
                    print()
        
        # Bước 5: Detailed analysis
        print("\n📈 Step 5: Detailed Analysis")
        print("-" * 50)
        
        # Kiểm tra consultant availability
        consultants_df = recommender.get_consultants_data()
        print(f"👨‍⚕️ Total consultants in database: {len(consultants_df)}")
        
        if not consultants_df.empty:
            available_consultants = consultants_df[consultants_df['is_available'] == True]
            print(f"✅ Available consultants: {len(available_consultants)}")
            
            # Show consultant specializations
            specializations = consultants_df['specialization'].value_counts()
            print(f"🏥 Consultant specializations:")
            for spec, count in specializations.head(5).items():
                print(f"   - {spec}: {count} consultants")
        
        # Kiểm tra user-consultant interaction matrix
        if not consultant_interactions.empty:
            unique_users = consultant_interactions['user_id'].nunique()
            unique_consultants = consultant_interactions['item_id'].nunique()
            print(f"\n📊 Interaction Matrix:")
            print(f"   - Unique users with consultant interactions: {unique_users}")
            print(f"   - Unique consultants with interactions: {unique_consultants}")
            print(f"   - Matrix density: {len(consultant_interactions)/(unique_users*unique_consultants)*100:.2f}%")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_debug_specific_user():
    """Debug specific user collaborative filtering"""
    print("\n🔍 DEBUG: Testing specific user step by step")
    print("=" * 70)
    
    try:
        db = SessionLocal()
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Lấy một user có survey data
        user_surveys = recommender.get_user_survey_data()
        if user_surveys.empty:
            print("❌ No survey data!")
            return
        
        test_user_id = user_surveys.iloc[0]['user_id']
        test_user_risk = user_surveys.iloc[0]['risk_level']
        
        print(f"🎯 Debug User: {test_user_id} (Risk: {test_user_risk})")
        
        # Step by step debug
        print("\n1️⃣ Finding users with same risk level...")
        users_same_risk = user_surveys[
            (user_surveys['risk_level'] == test_user_risk) &
            (user_surveys['user_id'] != test_user_id)
        ]['user_id'].unique().tolist()
        
        print(f"   👥 Found {len(users_same_risk)} users with {test_user_risk} risk")
        
        if len(users_same_risk) < 2:
            print("   ⚠️  Not enough similar users!")
            return
        
        print("2️⃣ Getting consultant interactions...")
        interactions_df = recommender.get_user_interactions()
        consultant_interactions = interactions_df[
            (interactions_df['item_type'] == 'consultant') &
            (interactions_df['user_id'].isin(users_same_risk + [test_user_id]))
        ]
        
        print(f"   📅 Found {len(consultant_interactions)} consultant interactions")
        
        if consultant_interactions.empty:
            print("   ❌ No consultant interactions!")
            return
        
        print("3️⃣ Creating user-consultant matrix...")
        user_consultant_matrix = consultant_interactions.pivot_table(
            index='user_id',
            columns='item_id', 
            values='rating',
            fill_value=0
        )
        
        print(f"   📊 Matrix shape: {user_consultant_matrix.shape}")
        print(f"   👤 Users in matrix: {list(user_consultant_matrix.index)}")
        print(f"   👨‍⚕️ Consultants in matrix: {list(user_consultant_matrix.columns)}")
        
        if test_user_id not in user_consultant_matrix.index:
            print(f"   ❌ Test user {test_user_id} not in matrix!")
            return
        
        print("4️⃣ Computing user similarity...")
        from sklearn.metrics.pairwise import cosine_similarity
        import pandas as pd
        
        user_similarity = cosine_similarity(user_consultant_matrix.values)
        user_similarity_df = pd.DataFrame(
            user_similarity,
            index=user_consultant_matrix.index,
            columns=user_consultant_matrix.index
        )
        
        similar_users = user_similarity_df[test_user_id].drop(test_user_id).sort_values(ascending=False)
        print(f"   🎯 Top 3 similar users:")
        for user, score in similar_users.head(3).items():
            print(f"      - {user}: {score:.3f}")
        
        print("5️⃣ Generating recommendations...")
        recommendations = recommender.collaborative_filtering_consultant_recommendations(
            user_id=test_user_id,
            top_k=3
        )
        
        print(f"   ✅ Generated {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['name']} (Score: {rec['predicted_rating']:.3f})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🧪 Collaborative Consultant Recommendations - Test Suite")
    print("=" * 70)
    
    # Test 1: Basic collaborative filtering test
    test_collaborative_consultant_recommendations()
    
    # Test 2: Debug specific user
    test_debug_specific_user()
    
    print("\n🎯 Test completed!")
    print("💡 Key points to check:")
    print("   1. Are there enough users with same risk level?")
    print("   2. Do similar users have consultant appointment history?")
    print("   3. Is the user-consultant interaction matrix sparse?")
    print("   4. Are similarity scores meaningful (> 0.1)?")
    print("   5. Are consultants still available for booking?")

if __name__ == "__main__":
    main()
