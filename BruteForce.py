
import requests
import time
import json
from datetime import datetime

URL = "https://dsapi.thelocal.co.in/dc/api/v1/auth/login"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Use an authorized QA test account
EMAIL = "security.test@example.com"

# Small number of controlled invalid attempts
TEST_PASSWORD = "Invalid-QA-Password"

MAX_ATTEMPTS = 3
DELAY = 5

results = []

print("=" * 60)
print("DOCSYNAPSE BRUTE FORCE PROTECTION TEST")
print("=" * 60)

for attempt in range(1, MAX_ATTEMPTS + 1):

    payload = {
        "email": EMAIL,
        "password": TEST_PASSWORD
    }

    print(f"\nAttempt: {attempt}")

    try:
        start = time.time()

        response = requests.post(
            URL,
            headers=HEADERS,
            json=payload,
            timeout=10
        )

        response_time = round(time.time() - start, 3)

        result = {
            "attempt": attempt,
            "timestamp": datetime.now().isoformat(),
            "status_code": response.status_code,
            "response_time": response_time,
            "response": response.text[:300],
            "retry_after": response.headers.get("Retry-After")
        }

        results.append(result)

        print("HTTP Status:", response.status_code)
        print("Response Time:", response_time, "seconds")
        print("Response:", response.text[:200])

        if response.status_code == 429:
            print("\nRATE LIMIT DETECTED")
            print("Login restriction appears active.")
            break

        if response.status_code in (423,):
            print("\nACCOUNT LOCKOUT RESPONSE DETECTED")
            break

        if response.status_code in (200, 201):
            print("\nUnexpected success. Stop and investigate.")
            break

        time.sleep(DELAY)

    except requests.exceptions.RequestException as error:
        print("Request Error:", error)
        break

# Save report
filename = "DocSynapse_BruteForce_Report.json"

with open(filename, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\n" + "=" * 60)
print("TEST FINISHED")
print("Attempts executed:", len(results))
print("Report:", filename)
print("=" * 60)
