
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

# Benign HTML injection test payloads.
# These are submitted as data, not executed as scripts.

TEST_CASES = [
    {
        "name": "Basic HTML heading",
        "value": "<h1>HTML_TEST</h1>"
    },
    {
        "name": "Bold HTML tag",
        "value": "<b>HTML_TEST</b>"
    },
    {
        "name": "Italic HTML tag",
        "value": "<i>HTML_TEST</i>"
    },
    {
        "name": "Paragraph HTML tag",
        "value": "<p>HTML_TEST</p>"
    },
    {
        "name": "HTML link",
        "value": '<a href="https://example.com">HTML_TEST</a>'
    },
    {
        "name": "HTML image",
        "value": '<img src="https://example.com/test.png" alt="HTML_TEST">'
    },
    {
        "name": "HTML table",
        "value": "<table><tr><td>HTML_TEST</td></tr></table>"
    },
    {
        "name": "HTML formatting",
        "value": "<strong>HTML_TEST</strong>"
    },
    {
        "name": "HTML div element",
        "value": '<div class="test">HTML_TEST</div>'
    },
    {
        "name": "HTML entity",
        "value": "&lt;h1&gt;HTML_TEST&lt;/h1&gt;"
    }
]

FIELDS = ["email", "password", "platform", "deviceId"]

print("=" * 65)
print("DOCSYNAPSE - HTML INJECTION SECURITY TESTING")
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
            body = response.text

            print("HTTP Status:", response.status_code)
            print("Response Time:", elapsed)

            if response.status_code == 429:
                print("RATE LIMIT DETECTED - STOPPING TEST")
                raise SystemExit

            if "HTML_TEST" in body:
                print("OBSERVATION: HTML marker reflected in API response")
            else:
                print("OBSERVATION: HTML marker not reflected")

            if response.status_code in (400, 401, 403, 422):
                print("VALIDATION: Request rejected")

            elif response.status_code >= 500:
                print("WARNING: SERVER ERROR - INVESTIGATE")

            print("Response:", body[:300])

        except requests.exceptions.RequestException as error:
            print("REQUEST ERROR:", error)
            raise SystemExit

        time.sleep(5)

print("\n" + "=" * 65)
print("HTML INJECTION TESTING COMPLETED")
print("=" * 65)
