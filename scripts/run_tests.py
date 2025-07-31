#!/usr/bin/env python3
"""Test runner script for Home Assistant testing framework."""
import subprocess
import sys
import os
import time
from pathlib import Path
import json
from datetime import datetime

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(message):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{message}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message):
    """Print warning message."""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def check_ha_ready():
    """Check if Home Assistant is ready."""
    import requests
    
    ha_url = os.getenv("HA_URL", "http://localhost:8123")
    max_attempts = 30
    
    print("Checking Home Assistant availability...")
    
    for i in range(max_attempts):
        try:
            response = requests.get(f"{ha_url}/api/", timeout=2)
            if response.status_code == 200:
                print_success("Home Assistant is ready!")
                return True
        except:
            pass
        
        if i < max_attempts - 1:
            print(f"  Waiting for Home Assistant... ({i+1}/{max_attempts})")
            time.sleep(2)
    
    print_error("Home Assistant is not available!")
    return False


def run_test_suite(test_type, timeout=300):
    """Run a specific test suite."""
    test_dir = f"tests/{test_type}"
    report_dir = f"reports/{test_type}"
    
    # Create report directory
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    
    # Build pytest command
    cmd = [
        "pytest",
        test_dir,
        "-v",
        "--tb=short",
        f"--cov=tests",
        f"--cov-report=html:{report_dir}/coverage",
        f"--cov-report=term",
        f"--junit-xml={report_dir}/results.xml",
        f"--html={report_dir}/report.html",
        "--self-contained-html"
    ]
    
    # Add markers for integration tests
    if test_type in ["integration", "ui", "api"]:
        cmd.append(f"-m={test_type}")
        cmd.append(f"--timeout={timeout}")
    
    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    # Parse results
    success = result.returncode == 0
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Summary
    if success:
        print_success(f"{test_type.upper()} tests completed in {duration:.2f}s")
    else:
        print_error(f"{test_type.upper()} tests failed!")
    
    return success, duration


def generate_summary_report(results):
    """Generate a summary report of all test results."""
    print_header("TEST SUMMARY REPORT")
    
    total_duration = sum(r[1] for r in results.values())
    all_passed = all(r[0] for r in results.values())
    
    # Test results table
    print(f"{'Test Suite':<20} {'Status':<15} {'Duration':<10}")
    print("-" * 45)
    
    for test_type, (passed, duration) in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"{test_type:<20} {status:<24} {duration:>6.2f}s")
    
    print("-" * 45)
    print(f"{'TOTAL':<20} {'':<15} {total_duration:>6.2f}s")
    
    # Overall status
    print(f"\n{BOLD}Overall Status: ", end="")
    if all_passed:
        print_success("ALL TESTS PASSED")
    else:
        print_error("SOME TESTS FAILED")
    
    # Coverage summary
    print(f"\n{BOLD}Coverage Reports:{RESET}")
    for test_type in results.keys():
        report_path = f"reports/{test_type}/coverage/index.html"
        if os.path.exists(report_path):
            print(f"  - {test_type}: {report_path}")
    
    # Save JSON summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "results": {
            test_type: {
                "passed": passed,
                "duration": duration
            }
            for test_type, (passed, duration) in results.items()
        },
        "total_duration": total_duration,
        "all_passed": all_passed
    }
    
    with open("reports/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    return all_passed


def main():
    """Main test runner function."""
    print_header("Home Assistant Test Runner")
    
    # Parse arguments
    test_types = ["unit", "integration", "ui", "api"]
    if len(sys.argv) > 1:
        test_types = sys.argv[1:]
    
    # Check for Home Assistant if running integration tests
    if any(t in ["integration", "ui", "api"] for t in test_types):
        if not check_ha_ready():
            print_error("Please start Home Assistant first: make start")
            sys.exit(1)
    
    # Run test suites
    results = {}
    
    for test_type in test_types:
        if test_type not in ["unit", "integration", "ui", "api"]:
            print_warning(f"Unknown test type: {test_type}")
            continue
        
        print_header(f"Running {test_type.upper()} Tests")
        
        # Check if test directory exists
        test_dir = f"tests/{test_type}"
        if not os.path.exists(test_dir):
            print_warning(f"Test directory not found: {test_dir}")
            results[test_type] = (False, 0)
            continue
        
        # Check if tests exist
        test_files = list(Path(test_dir).glob("test_*.py"))
        if not test_files:
            print_warning(f"No tests found in {test_dir}")
            results[test_type] = (True, 0)
            continue
        
        print(f"Found {len(test_files)} test file(s)")
        
        # Run tests
        passed, duration = run_test_suite(test_type)
        results[test_type] = (passed, duration)
        
        # Small delay between test suites
        if test_type != test_types[-1]:
            time.sleep(1)
    
    # Generate summary report
    all_passed = generate_summary_report(results)
    
    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()