
import requests
import time
import json
from datetime import datetime

URL = "https://dsapi.thelocal.co.in/dc/api/v1/auth/login"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Replace with approved QA test accounts.
# Both accounts must be under your control.
TEST_ACCOUNTS = [
    {
        "name": "QA account A",
        "email": "qa_existing@example.com",
        "password": "Invalid-QA-Password"
    },
    {
        "name": "QA account B",
        "email": "qa_nonexisting@example.com",
        "password": "Invalid-QA-Password"
    }
]

results = []

print("=" * 65)
print("DOCSYNAPSE USERNAME ENUMERATION TEST")
print("=" * 65)

for account in TEST_ACCOUNTS:

    payload = {
        "email": account["email"],
        "password": account["password"]
    }

    print("\nTesting:", account["name"])

    try:
        start = time.perf_counter()

        response = requests.post(
            URL,
            headers=HEADERS,
            json=payload,
            timeout=10
        )

        elapsed = round(
            time.perf_counter() - start, 4
        )

        result = {
            "account": account["name"],
            "http_status": response.status_code,
            "response_time": elapsed,
            "response_body": response.text[:500],
            "timestamp": datetime.now().isoformat()
        }

        results.append(result)

        print("HTTP Status:", response.status_code)
        print("Response Time:", elapsed)
        print("Response:", response.text[:300])

        if response.status_code == 429:
            print("Rate limit detected. Stopping.")
            break

        time.sleep(3)

    except requests.exceptions.RequestException as error:
        print("Request error:", error)
        break

# Compare responses
if len(results) == 2:

    first = results[0]
    second = results[1]

    print("\n" + "=" * 65)
    print("ENUMERATION COMPARISON")
    print("=" * 65)

    if first["http_status"] != second["http_status"]:
        print("WARNING: Different HTTP status codes.")
        print("Investigate possible username enumeration.")

    elif first["response_body"] != second["response_body"]:
        print("WARNING: Different response bodies.")
        print("Investigate possible username enumeration.")

    else:
        print("No obvious response difference detected.")

    print("Note: Timing differences also require analysis.")

filename = "DocSynapse_Username_Enumeration_Report.json"

with open(filename, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\nReport saved:", filename)
