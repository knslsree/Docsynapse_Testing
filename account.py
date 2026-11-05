
import os
import time
import requests
from urllib.parse import quote

# --------------------------------------------------
# DOCSYNAPSE QA CONFIGURATION
# --------------------------------------------------

BASE_URL = os.getenv(
    "DOCSYNAPSE_QA_ENVIRONMENT",
    "https://qadsapi.thelocal.co.in"
).rstrip("/")

API_BASE = BASE_URL + "/dc/api/v1"
LOGIN_URL = API_BASE + "/auth/login"

# IMPORTANT:
# Replace this placeholder with the actual GET endpoint
# from your DocSynapse Swagger/Postman documentation.
RESOURCE_ENDPOINT = API_BASE + "/records/{record_id}"

USER_A = os.getenv("DOCSYNAPSE_QA_USER_A")
PASSWORD_A = os.getenv("DOCSYNAPSE_QA_PASSWORD_A")

USER_B = os.getenv("DOCSYNAPSE_QA_USER_B")
PASSWORD_B = os.getenv("DOCSYNAPSE_QA_PASSWORD_B")

RECORD_A = os.getenv("DOCSYNAPSE_QA_RECORD_A")
RECORD_B = os.getenv("DOCSYNAPSE_QA_RECORD_B")

TIMEOUT = 15

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Content-Type": "application/json"
})


# --------------------------------------------------
# LOGIN FUNCTION
# --------------------------------------------------

def login(username, password):

    response = session.post(
        LOGIN_URL,
        json={
            "email": username,
            "password": password
        },
        timeout=TIMEOUT
    )

    print("Login HTTP status:", response.status_code)

    if response.status_code == 429:
        raise RuntimeError("Rate limited. Stopping tests.")

    if response.status_code != 200:
        raise RuntimeError("Login failed. Check QA credentials/API response.")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Login response was not valid JSON.")

    # Adjust this extraction to match the actual login response.
    token = (
        data.get("data", {}).get("accessToken")
        or data.get("accessToken")
        or data.get("token")
    )

    if not token:
        raise RuntimeError(
            "Access token not found. Check the documented login response format."
        )

    return token


# --------------------------------------------------
# RESOURCE ACCESS TEST
# --------------------------------------------------

def test_resource(label, record_id, token=None):

    url = RESOURCE_ENDPOINT.format(
        record_id=quote(str(record_id), safe="")
    )

    headers = {}

    if token:
        headers["Authorization"] = "Bearer " + token

    response = session.get(
        url,
        headers=headers,
        timeout=TIMEOUT
    )

    print("\nTest:", label)
    print("HTTP status:", response.status_code)
    print("Response time:", round(response.elapsed.total_seconds(), 3), "seconds")

    if response.status_code == 429:
        raise RuntimeError("Rate limited. Stopping tests.")

    if response.status_code == 200:
        print("RESULT: Access granted.")
        print("Review whether this account is authorized for this resource.")
    elif response.status_code in (401, 403, 404):
        print("RESULT: Access denied or resource hidden.")
    else:
        print("RESULT: Unexpected response. Investigate API behavior.")


# --------------------------------------------------
# MAIN TESTS
# --------------------------------------------------

def main():

    required = {
        "DOCSYNAPSE_QA_USER_A": USER_A,
        "DOCSYNAPSE_QA_PASSWORD_A": PASSWORD_A,
        "DOCSYNAPSE_QA_USER_B": USER_B,
        "DOCSYNAPSE_QA_PASSWORD_B": PASSWORD_B,
        "DOCSYNAPSE_QA_RECORD_A": RECORD_A,
        "DOCSYNAPSE_QA_RECORD_B": RECORD_B
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        print("Missing environment variables:")
        for key in missing:
            print("-", key)
        return

    print("DOCSYNAPSE BROKEN ACCESS CONTROL TEST")
    print("-------------------------------------")

    token_a = login(USER_A, PASSWORD_A)
    time.sleep(2)

    token_b = login(USER_B, PASSWORD_B)
    time.sleep(2)

    # Test 1: No authentication
    test_resource(
        "Unauthenticated user accessing Account A record",
        RECORD_A
    )

    time.sleep(2)

    # Test 2: Account A accessing its own record
    test_resource(
        "Account A accessing its own record",
        RECORD_A,
        token_a
    )

    time.sleep(2)

    # Test 3: Account B accessing its own record
    test_resource(
        "Account B accessing its own record",
        RECORD_B,
        token_b
    )

    time.sleep(2)

    # Test 4: Account B attempting to access Account A record
    test_resource(
        "Account B accessing Account A record",
        RECORD_A,
        token_b
    )

    time.sleep(2)

    # Test 5: Account A attempting to access Account B record
    test_resource(
        "Account A accessing Account B record",
        RECORD_B,
        token_a
    )

    print("\n-------------------------------------")
    print("TEST COMPLETED")
    print("Review authorization and resource ownership.")
    print("-------------------------------------")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        print("Network/API error:", type(error).__name__)
    except RuntimeError as error:
        print("STOPPED:", error)
