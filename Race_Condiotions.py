
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================
# DOCSYNAPSE RACE CONDITION TEST
# ==========================================

BASE_URL = input("Enter Base URL: ").strip().rstrip("/")
API_ID = input("Enter API ID: ").strip()
DOCTOR_ID = input("Enter Target Doctor ID: ").strip()
TOKEN = input("Enter Bearer Token: ").strip()

TOTAL_REQUESTS = 10

URL = f"{BASE_URL}/api/v1/network/connections/send"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

PAYLOAD = {
    "targetDoctorId": DOCTOR_ID
}

barrier = threading.Barrier(TOTAL_REQUESTS)


def send_request(request_number):

    try:
        barrier.wait(timeout=20)

        response = requests.post(
            URL,
            headers=HEADERS,
            json=PAYLOAD,
            timeout=30
        )

        return {
            "request": request_number,
            "status": response.status_code,
            "response": response.text[:500]
        }

    except Exception as error:

        return {
            "request": request_number,
            "status": "ERROR",
            "response": str(error)
        }


def main():

    print("\n===================================")
    print("DOCSYNAPSE RACE CONDITION TEST")
    print("===================================")

    print("API ID:", API_ID)
    print("Target Doctor ID:", DOCTOR_ID)
    print("Concurrent Requests:", TOTAL_REQUESTS)

    print("\nStarting simultaneous API requests...\n")

    results = []

    with ThreadPoolExecutor(
        max_workers=TOTAL_REQUESTS
    ) as executor:

        futures = [
            executor.submit(send_request, i + 1)
            for i in range(TOTAL_REQUESTS)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: x["request"])

    success = 0

    for result in results:

        print("-----------------------------------")
        print("Request:", result["request"])
        print("HTTP Status:", result["status"])
        print("Response:", result["response"])

        if isinstance(result["status"], int):
            if 200 <= result["status"] < 300:
                success += 1

    print("\n===================================")
    print("TEST SUMMARY")
    print("===================================")

    print("Total Requests:", TOTAL_REQUESTS)
    print("Successful Responses:", success)

    if success > 1:
        print("WARNING: Multiple successful responses.")
        print("Verify duplicate records in database.")
    elif success == 1:
        print("One successful response.")
        print("Verify duplicate prevention.")
    else:
        print("No successful response. Check API configuration.")

    print("\nTest completed.")


if __name__ == "__main__":
    main()
