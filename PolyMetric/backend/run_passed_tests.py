#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test runner for passed PolyMetric API tests
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function"""
    # Change to project directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("PolyMetric API Test Runner (Passed Tests Only)")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        valid_modules = {
            "users": "test_users_api",
            "datasets": "test_datasets_api",
            "models": "test_models_api",
            "tasks": "test_tasks_api",
            "user": "test_users_api",
            "dataset": "test_datasets_api",
            "model": "test_models_api",
            "task": "test_tasks_api"
        }
        
        if module_name.lower() in valid_modules:
            module = valid_modules[module_name.lower()]
            print(f"Running module: {module}")
            print('#'*60)
            
            cmd = f"python manage.py test tests.{module} --settings=PolyMetric.test_settings --verbosity=1"
            result = subprocess.run(cmd, shell=True)
            
            if result.returncode == 0:
                print(f"\nSuccess: {module} tests passed!")
                return 0
            else:
                print(f"\nError: {module} tests failed")
                return 1
        else:
            print(f"Error: Unknown module '{module_name}'")
            print("Available modules: users, datasets, models, tasks")
            return 1
    else:
        # Run all tests that are known to pass
        test_modules = [
            "test_users_api",
            "test_datasets_api",
            "test_models_api",
            "test_tasks_api"
        ]
        
        all_passed = True
        for module in test_modules:
            print(f"\n{'#'*60}")
            print(f"Running module: {module}")
            print('#'*60)
            
            cmd = f"python manage.py test tests.{module} --settings=PolyMetric.test_settings --verbosity=1"
            result = subprocess.run(cmd, shell=True)
            
            if result.returncode != 0:
                all_passed = False
                print(f"FAILED: {module}")
            else:
                print(f"PASSED: {module}")
        
        print(f"\n{'#'*60}")
        if all_passed:
            print("Success: All tests passed!")
            return 0
        else:
            print("Error: Some tests failed")
            return 1

if __name__ == "__main__":
    sys.exit(main())