#!/usr/bin/env python3
"""
Quick test runner for the hybrid recommendation system
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    try:
        from test_hybrid_recommendations import test_hybrid_recommendations, test_score_normalization, test_hybrid_score_calculation
        
        print("🧪 Running Hybrid Recommendation System Tests")
        print("=" * 60)
        
        # Run individual tests
        print("\n1. Testing Score Normalization...")
        test_score_normalization()
        
        print("\n2. Testing Hybrid Score Calculation...")
        test_hybrid_score_calculation()
        
        print("\n3. Testing Full Hybrid Recommendation System...")
        result = test_hybrid_recommendations()
        
        if result and result.get('status') == 'success':
            print("\n✅ ALL TESTS PASSED! Hybrid recommendation system is working correctly.")
        else:
            print("\n⚠️ Some tests had issues. Check the output above for details.")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have set up the Python environment and database connection properly.")
        print("Run 'pip install -r requirements.txt' if needed.")
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
