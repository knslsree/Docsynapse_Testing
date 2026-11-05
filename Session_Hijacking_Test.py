
import requests
import json
import os
from datetime import datetime

# Read QA environment URL
BASE_URL = os.getenv(
    "DOCSYNAPSE_QA_ENVIRONMENT",
    "https://qadsapi.thelocal.co.in"
).rstrip("/")

API_BASE = BASE_URL + "/dc/api/v1"

LOGIN_URL = API_BASE + "/auth/login"

# Replace with the actual protected endpoint
PROTECTED_URL = API_BASE + "/auth/me"

EMAIL = "security.test@example.com"

PASSWORD = os.getenv("DOCSYNAPSE_QA_PASSWORD")

results = []

def record(name, response):
    results.append({
        "test": name,
        "status": response.status_code,
        "response_time": response.elapsed.total_seconds(),
        "timestamp": datetime.now().isoformat(),
        "response": response.text[:300]
    })

    print("\nTest:", name)
    print("HTTP Status:", response.status_code)
    print("Response:", response.text[:200])


print("=" * 60)
print("DOCSYNAPSE SESSION SECURITY TEST")
print("=" * 60)

print("QA Environment:", BASE_URL)

if not PASSWORD:
    raise SystemExit(
        "Set DOCSYNAPSE_QA_PASSWORD before running."
    )

session = requests.Session()

try:
    # TEST 1: Login
    login = session.post(
        LOGIN_URL,
        json={
            "email": EMAIL,
            "password": PASSWORD
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        timeout=10
    )

    record("QA Login", login)

    if login.status_code == 429:
        raise SystemExit("Rate limited. Stopping.")

    if login.status_code not in (200, 201):
        raise SystemExit("Login unsuccessful.")

    # TEST 2: Authenticated access
    protected = session.get(
        PROTECTED_URL,
        timeout=10
    )

    record("Authenticated request", protected)

    # TEST 3: Unauthenticated access
    unauthenticated = requests.get(
        PROTECTED_URL,
        timeout=10
    )

    record("Unauthenticated request", unauthenticated)

    # TEST 4: Invalid token
    invalid = requests.get(
        PROTECTED_URL,
        headers={
            "Authorization": "Bearer INVALID_QA_TOKEN"
        },
        timeout=10
    )

    record("Invalid token request", invalid)

except requests.RequestException as error:
    print("Request error:", error)

finally:
    session.close()

    with open(
        "DocSynapse_Session_Security_Report.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(results, file, indent=4)

    print("\nReport generated successfully.")
