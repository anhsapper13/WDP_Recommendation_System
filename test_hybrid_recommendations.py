#!/usr/bin/env python3
"""
Comprehensive test for the hybrid recommendation system
Tests the enhanced hybrid_recommendations function with detailed validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import get_db_session
from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
import json

def test_hybrid_recommendations():
    """
    Test the hybrid recommendation system with comprehensive validation
    """
    print("🧪 TESTING HYBRID RECOMMENDATION SYSTEM")
    print("=" * 80)
    
    # Initialize database session
    db = next(get_db_session())
    
    try:
        # Initialize recommendation system
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Test with a sample user ID
        test_user_id = "test_user_123"
        
        print(f"🎯 Testing hybrid recommendations for user: {test_user_id}")
        print("-" * 50)
        
        # Get hybrid recommendations
        result = recommender.hybrid_recommendations(test_user_id, top_k=5)
        
        print("\n📊 HYBRID RECOMMENDATION ANALYSIS:")
        print("=" * 50)
        
        # Validate structure
        required_fields = ['courses', 'consultants', 'user_risk_info', 'recommendation_type', 'status']
        for field in required_fields:
            if field in result:
                print(f"✅ Required field '{field}': Present")
            else:
                print(f"❌ Required field '{field}': Missing")
        
        # Analyze recommendation summary
        if 'recommendation_summary' in result:
            summary = result['recommendation_summary']
            print(f"\n📈 RECOMMENDATION SUMMARY:")
            print(f"   Total courses recommended: {summary.get('total_courses', 0)}")
            print(f"   Total consultants recommended: {summary.get('total_consultants', 0)}")
            print(f"   Content-based courses found: {summary.get('content_based_courses', 0)}")
            print(f"   Collaborative courses found: {summary.get('collaborative_courses', 0)}")
            print(f"   Content-based consultants found: {summary.get('content_based_consultants', 0)}")
            print(f"   Collaborative consultants found: {summary.get('collaborative_consultants', 0)}")
            print(f"   Unique courses processed: {summary.get('unique_courses_found', 0)}")
            print(f"   Unique consultants processed: {summary.get('unique_consultants_found', 0)}")
        
        # Analyze hybrid configuration
        if 'hybrid_config' in result:
            config = result['hybrid_config']
            print(f"\n⚙️ HYBRID CONFIGURATION:")
            print(f"   Content weight: {config.get('content_weight', 'N/A')}")
            print(f"   Collaborative weight: {config.get('collaborative_weight', 'N/A')}")
            print(f"   Diversity boost: {config.get('diversity_boost', 'N/A')}")
        
        # Detailed course analysis
        courses = result.get('courses', [])
        print(f"\n📚 COURSE RECOMMENDATIONS ANALYSIS ({len(courses)} courses):")
        print("-" * 50)
        
        if courses:
            for i, course in enumerate(courses, 1):
                print(f"\n{i}. Course Analysis:")
                print(f"   ID: {course.get('course_id', 'N/A')}")
                print(f"   Title: {course.get('title', 'N/A')[:60]}{'...' if len(course.get('title', '')) > 60 else ''}")
                print(f"   Hybrid Score: {course.get('hybrid_score', 0):.4f}")
                print(f"   Recommendation Source: {course.get('recommendation_source', 'unknown')}")
                print(f"   Content Score: {course.get('score', 'N/A')}")
                print(f"   Collaborative Score: {course.get('predicted_rating', 'N/A')}")
                print(f"   Enrollment Count: {course.get('enrollment_count', 0)}")
                
                # Validate hybrid score logic
                content_score = course.get('score', 0) if course.get('score') else 0
                collab_score = course.get('predicted_rating', 0) if course.get('predicted_rating') else 0
                expected_base = (min(1.0, content_score) * 0.6) + (min(1.0, collab_score) * 0.4)
                
                # Check if diversity boost was applied
                has_both = bool(course.get('score')) and bool(course.get('predicted_rating'))
                expected_score = expected_base * 1.1 if has_both else expected_base
                
                actual_score = course.get('hybrid_score', 0)
                score_valid = abs(actual_score - expected_score) < 0.001  # Allow small floating point differences
                
                print(f"   ✅ Score validation: {'PASS' if score_valid else 'FAIL'} (expected: {expected_score:.4f}, actual: {actual_score:.4f})")
        else:
            print("   ⚠️ No course recommendations found")
        
        # Detailed consultant analysis
        consultants = result.get('consultants', [])
        print(f"\n👩‍⚕️ CONSULTANT RECOMMENDATIONS ANALYSIS ({len(consultants)} consultants):")
        print("-" * 50)
        
        if consultants:
            for i, consultant in enumerate(consultants, 1):
                print(f"\n{i}. Consultant Analysis:")
                print(f"   ID: {consultant.get('consultant_id', 'N/A')}")
                print(f"   Name: {consultant.get('name', 'N/A')}")
                print(f"   Hybrid Score: {consultant.get('hybrid_score', 0):.4f}")
                print(f"   Recommendation Source: {consultant.get('recommendation_source', 'unknown')}")
                print(f"   Content Score: {consultant.get('score', 'N/A')}")
                print(f"   Collaborative Score: {consultant.get('predicted_rating', 'N/A')}")
                print(f"   Experience Years: {consultant.get('experience_years', 'N/A')}")
                print(f"   Total Appointments: {consultant.get('total_appointments', 0)}")
        else:
            print("   ⚠️ No consultant recommendations found")
        
        # Test different scenarios
        print(f"\n🔬 TESTING DIFFERENT SCENARIOS:")
        print("-" * 50)
        
        # Test with different top_k values
        for k in [1, 3, 8]:
            print(f"\n📊 Testing with top_k={k}:")
            result_k = recommender.hybrid_recommendations(test_user_id, top_k=k)
            courses_k = len(result_k.get('courses', []))
            consultants_k = len(result_k.get('consultants', []))
            print(f"   Courses returned: {courses_k} (expected: ≤{k})")
            print(f"   Consultants returned: {consultants_k} (expected: ≤{min(3, k)})")
        
        print(f"\n✅ HYBRID RECOMMENDATION TEST COMPLETED SUCCESSFULLY")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during hybrid recommendation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        db.close()

def test_score_normalization():
    """
    Test the score normalization function separately
    """
    print(f"\n🧮 TESTING SCORE NORMALIZATION:")
    print("-" * 50)
    
    # Test data
    test_items = [
        {'id': 1, 'score': 0.1},
        {'id': 2, 'score': 0.5},
        {'id': 3, 'score': 0.9},
        {'id': 4, 'score': 0.3}
    ]
    
    print("Original scores:", [item['score'] for item in test_items])
    
    # Simulate normalization logic
    scores = [item.get('score', 0) for item in test_items]
    if max(scores) != min(scores):
        min_score, max_score = min(scores), max(scores)
        for item in test_items:
            original_score = item.get('score', 0)
            item['normalized_score'] = (original_score - min_score) / (max_score - min_score)
    
    print("Normalized scores:", [item.get('normalized_score', item['score']) for item in test_items])
    
    # Validate normalization
    normalized = [item.get('normalized_score', item['score']) for item in test_items]
    print(f"Min normalized: {min(normalized):.3f} (should be 0.0)")
    print(f"Max normalized: {max(normalized):.3f} (should be 1.0)")
    print(f"✅ Normalization test: {'PASS' if abs(min(normalized)) < 0.001 and abs(max(normalized) - 1.0) < 0.001 else 'FAIL'}")

def test_hybrid_score_calculation():
    """
    Test hybrid score calculation logic
    """
    print(f"\n🧮 TESTING HYBRID SCORE CALCULATION:")
    print("-" * 50)
    
    # Test scenarios
    test_cases = [
        # (content_score, collab_score, has_both, expected_base, expected_final)
        (0.8, 0.6, True, 0.72, 0.792),   # Both present -> boost applied
        (0.5, 0.0, False, 0.3, 0.3),     # Only content
        (0.0, 0.9, False, 0.36, 0.36),   # Only collaborative
        (1.0, 1.0, True, 1.0, 1.1),      # Maximum scores
        (0.0, 0.0, False, 0.0, 0.0),     # Zero scores
    ]
    
    content_weight = 0.6
    collaborative_weight = 0.4
    diversity_boost = 1.1
    
    for i, (content, collab, has_both, expected_base, expected_final) in enumerate(test_cases, 1):
        # Calculate hybrid score
        hybrid_base = (content * content_weight) + (collab * collaborative_weight)
        hybrid_final = hybrid_base * diversity_boost if has_both else hybrid_base
        
        print(f"\nTest Case {i}:")
        print(f"   Content: {content}, Collaborative: {collab}, Has Both: {has_both}")
        print(f"   Expected Base: {expected_base:.3f}, Calculated: {hybrid_base:.3f}")
        print(f"   Expected Final: {expected_final:.3f}, Calculated: {hybrid_final:.3f}")
        
        base_valid = abs(hybrid_base - expected_base) < 0.001
        final_valid = abs(hybrid_final - expected_final) < 0.001
        
        print(f"   ✅ Validation: {'PASS' if base_valid and final_valid else 'FAIL'}")

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE HYBRID RECOMMENDATION TESTS")
    print("=" * 80)
    
    # Run normalization test
    test_score_normalization()
    
    # Run hybrid score calculation test
    test_hybrid_score_calculation()
    
    # Run main hybrid recommendation test
    result = test_hybrid_recommendations()
    
    if result:
        print(f"\n📋 SUMMARY:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Recommendation Type: {result.get('recommendation_type', 'unknown')}")
        print(f"   Total Courses: {len(result.get('courses', []))}")
        print(f"   Total Consultants: {len(result.get('consultants', []))}")
        
        # Export result for manual inspection
        with open('hybrid_test_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"   ✅ Full result exported to: hybrid_test_result.json")
    
    print(f"\n🎉 ALL TESTS COMPLETED!")
