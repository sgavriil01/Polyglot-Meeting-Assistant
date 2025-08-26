#!/usr/bin/env python3

import sys
import os
import subprocess
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"\n🧪 Running: {test_file}")
    print("=" * 60)
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, test_file
        ], 
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file} - PASSED")
            if result.stdout:
                print(result.stdout[-500:])  # Last 500 chars of output
            return True
        else:
            print(f"❌ {test_file} - FAILED")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file} - TIMEOUT (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ {test_file} - ERROR: {e}")
        return False

def run_all_tests():
    """Run all test files in the tests directory"""
    print("🚀 POLYGLOT MEETING ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Get all test files
    test_files = [
        'test_search_simple.py',
        'test_search_engine.py', 
        'test_search_advanced.py',
        'test_comprehensive_validation.py',
        'test_edge_cases.py',
        'test_improved_nlp.py',
        'test_real_world_scenarios.py',
        'test_final_improvements.py'
    ]
    
    # Filter to only existing files
    existing_tests = []
    for test_file in test_files:
        if os.path.exists(test_file):
            existing_tests.append(test_file)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print(f"📋 Found {len(existing_tests)} test files to run")
    
    # Run tests
    start_time = time.time()
    passed = 0
    failed = 0
    
    for test_file in existing_tests:
        if run_test_file(test_file):
            passed += 1
        else:
            failed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Summary
    print("\n" + "=" * 80)
    print("🏆 TEST SUITE SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print(f"⏱️  Time: {total_time:.2f} seconds")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("🚀 Polyglot Meeting Assistant is ready for production!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
    
    return failed == 0

def run_demo():
    """Run the search explanation demo"""
    print("\n🎬 RUNNING SEARCH ENGINE DEMO")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 'search_explanation_demo.py'
        ],
        cwd=os.path.dirname(__file__),
        capture_output=True,
        text=True,
        timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Demo completed successfully!")
            print("\n📺 Demo Output:")
            print(result.stdout)
        else:
            print("❌ Demo failed")
            if result.stderr:
                print(result.stderr)
                
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            run_demo()
        elif sys.argv[1] == "help":
            print("""
🧪 Polyglot Meeting Assistant Test Runner

Usage:
  python run_all_tests.py          # Run all tests
  python run_all_tests.py demo     # Run search engine demo
  python run_all_tests.py help     # Show this help

Available tests:
  - test_search_simple.py          # Basic search functionality
  - test_search_engine.py          # Comprehensive search tests
  - test_search_advanced.py        # Advanced features and edge cases
  - test_comprehensive_validation.py # Full system validation
  - test_edge_cases.py             # Error handling and edge cases
  - test_improved_nlp.py           # NLP processing tests
  - test_real_world_scenarios.py   # Real-world usage scenarios
  - test_final_improvements.py     # Final system improvements
            """)
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Use 'help' to see available commands")
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)
