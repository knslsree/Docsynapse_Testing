import requests
import json

def check_api(url):
    headers = {
        "User-Agent": "API-Security-Checker/1.0"
    }

    print("\nChecking API:", url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        print("Status Code:", response.status_code)

        if response.status_code == 200:
            print("[INFO] API accessible without authentication")

            try:
                print(
                    json.dumps(
                        response.json(),
                        indent=4
                    )[:2000]
                )
            except ValueError:
                print("Response is not JSON.")

        elif response.status_code == 401:
            print("[SAFE] Authentication required.")

        elif response.status_code == 403:
            print("[INFO] Access forbidden.")

        else:
            print("Response:", response.status_code)

    except requests.exceptions.RequestException as error:
        print("Request failed:", error)


if __name__ == "__main__":
    target = input("Enter authorized API URL: ")
    check_api(target)