
import requests
import time
import csv
from datetime import datetime

# DocSynapse Dev API
URL = "https://qadsapi.thelocal.co.in/dc"

# Configure timeout threshold
TIMEOUT_SECONDS = 5

# Number of controlled test requests
TOTAL_REQUESTS = 10

results = []

print("=" * 65)
print("DOCSYNAPSE - API TIMEOUT VALIDATION")
print("=" * 65)

print("Target:", URL)
print("Timeout threshold:", TIMEOUT_SECONDS, "seconds")
print("Total requests:", TOTAL_REQUESTS)
print("-" * 65)

for i in range(1, TOTAL_REQUESTS + 1):

    start_time = time.perf_counter()

    try:
        response = requests.get(
            URL,
            timeout=TIMEOUT_SECONDS
        )

        elapsed = time.perf_counter() - start_time

        if elapsed >= TIMEOUT_SECONDS * 0.8:
            status = "WARNING - SLOW RESPONSE"
        else:
            status = "COMPLETED"

        print(
            f"Test {i}: HTTP {response.status_code} | "
            f"Time: {elapsed:.3f}s | {status}"
        )

        results.append([
            i,
            response.status_code,
            round(elapsed, 3),
            status
        ])

    except requests.Timeout:

        elapsed = time.perf_counter() - start_time

        print(
            f"Test {i}: TIMEOUT | "
            f"Time: {elapsed:.3f}s"
        )

        results.append([
            i,
            "TIMEOUT",
            round(elapsed, 3),
            "FAIL"
        ])

    except requests.RequestException as error:

        elapsed = time.perf_counter() - start_time

        print("Request error:", error)

        results.append([
            i,
            "ERROR",
            round(elapsed, 3),
            "ERROR"
        ])

    time.sleep(1)

# Export test results
filename = "api_timeout_results.csv"

with open(filename, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Test Number",
        "HTTP Status",
        "Response Time (Seconds)",
        "Result"
    ])

    writer.writerows(results)

print("\n" + "=" * 65)
print("TEST SUMMARY")
print("=" * 65)

completed = sum(1 for r in results if r[3] == "COMPLETED")
slow = sum(1 for r in results if r[3] == "WARNING - SLOW RESPONSE")
failed = sum(1 for r in results if r[3] in ("FAIL", "ERROR"))

print("Completed:", completed)
print("Slow responses:", slow)
print("Timeouts/errors:", failed)

print("\nResults exported to:", filename)
print("Execution completed:", datetime.now())
