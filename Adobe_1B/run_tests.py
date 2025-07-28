#!/usr/bin/env python3


import subprocess
import sys

def run_tests():
    """Run the test suite."""
    print("🧪 Running Adobe Hackathon Round 1B Solution Tests\n")
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test_solution.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("\n📋 Test Output:")
            print(result.stdout)
        else:
            print("❌ Tests failed!")
            print("\n📋 Test Output:")
            print(result.stdout)
            print("\n❌ Error Output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 