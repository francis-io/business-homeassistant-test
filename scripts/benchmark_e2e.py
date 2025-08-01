#!/usr/bin/env python3
"""
Benchmark E2E tests by running them multiple times and calculating statistics.

Usage:
    python scripts/benchmark_e2e.py [number_of_runs]

Default is 20 runs.
"""

import json
import re
import statistics
import subprocess
import sys
import time


def run_e2e_test() -> tuple[float, str]:
    """Run E2E test once and return execution time and test results."""
    start_time = time.time()

    # Run the test using make
    result = subprocess.run(["make", "test:e2e"], capture_output=True, text=True)

    end_time = time.time()
    execution_time = end_time - start_time

    # Extract test results from output
    test_results = ""
    for line in result.stdout.split("\n"):
        if re.search(r"\d+ passed.*\d+ skipped.*warnings", line):
            test_results = line.strip()
            break

    return execution_time, test_results


def print_statistics(times: list[float], runs: int, last_test_results: str):
    """Calculate and print statistics for the benchmark runs."""
    print("\n📊 Results Summary")
    print("==================")

    # Basic statistics
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)

    print("\nTotal E2E test execution time (full cycle):")
    print(f"  Runs:    {runs}")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min:     {min_time:.3f}s")
    print(f"  Max:     {max_time:.3f}s")

    if len(times) >= 2:
        std_dev = statistics.stdev(times)
        print(f"  Std Dev: {std_dev:.3f}s")

        # 95% Confidence Interval
        stderr = std_dev / (len(times) ** 0.5)
        ci_margin = stderr * 1.96
        ci_lower = avg_time - ci_margin
        ci_upper = avg_time + ci_margin
        print(f"\n95% Confidence Interval: {ci_lower:.3f}s - {ci_upper:.3f}s")

    # Percentiles
    print("\nPercentiles:")
    sorted_times = sorted(times)

    if len(times) >= 2:
        median = statistics.median(sorted_times)
        print(f"  50th (median): {median:.3f}s")

    if len(times) >= 10:
        p90_idx = int(len(times) * 0.9) - 1
        print(f"  90th:          {sorted_times[p90_idx]:.3f}s")

    if len(times) >= 20:
        p95_idx = int(len(times) * 0.95) - 1
        print(f"  95th:          {sorted_times[p95_idx]:.3f}s")

    # Show individual times
    print("\nIndividual run times:")
    for i, time_val in enumerate(times, 1):
        print(f"  Run {i:2d}: {time_val:.3f}s")

    # Test results
    print("\nTest results (from last run):")
    print(f"  {last_test_results}")

    # Save detailed results
    results = {
        "runs": runs,
        "times": times,
        "statistics": {
            "mean": avg_time,
            "min": min_time,
            "max": max_time,
            "std_dev": std_dev if len(times) >= 2 else None,
            "median": statistics.median(sorted_times) if len(times) >= 2 else None,
        },
        "last_test_results": last_test_results,
    }

    with open("e2e_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nDetailed results saved to: e2e_benchmark_results.json")


def main():
    """Run the benchmark with the specified number of iterations."""
    # Get number of runs from command line or use default
    runs = 20
    if len(sys.argv) > 1:
        try:
            runs = int(sys.argv[1])
            if runs < 1:
                raise ValueError("Number of runs must be positive")
        except ValueError as e:
            print(f"Error: {e}")
            print("Usage: python scripts/benchmark_e2e.py [number_of_runs]")
            sys.exit(1)

    print("🏃 E2E Test Benchmark")
    print("====================")
    print(f"Running E2E tests {runs} times to calculate average execution time")
    print()

    # Clean up before starting
    subprocess.run(
        ["docker-compose", "-f", "tests/e2e/docker/docker-compose.yml", "down"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
    )

    times = []
    last_test_results = ""

    # Run the tests
    for i in range(1, runs + 1):
        print(f"Run {i}/{runs}: ", end="", flush=True)

        try:
            execution_time, test_results = run_e2e_test()
            times.append(execution_time)
            last_test_results = test_results

            print(f"{test_results}  Time: {execution_time:.3f}s")

            # Small delay between runs
            if i < runs:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⚠️  Benchmark interrupted by user")
            if times:
                print(f"Showing statistics for {len(times)} completed runs:")
                print_statistics(times, len(times), last_test_results)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Print statistics
    print_statistics(times, runs, last_test_results)


if __name__ == "__main__":
    main()
