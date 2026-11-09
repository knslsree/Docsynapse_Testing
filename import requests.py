import requests

def test_login():
    # 1. Define the endpoint URL
    url = "https://devdocsynapse.thelocal.co.in/dc/api/v1/auth/login"

    # 2. Define your login credentials / payload
    # Update these keys ("email", "password" or "username", etc.) to match what your backend expects
    payload = {
        "email": "your_test_user@example.com",
        "password": "your_password_here"
    }

    # 3. Set headers to specify you are sending and expecting JSON
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"Sending POST request to: {url}\n")

    try:
        # 4. Make the POST request (use requests.get if your endpoint is configured as a GET)
        response = requests.post(url, json=payload, headers=headers)

        # 5. Print out response metadata
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print("-" * 50)

        # 6. Handle the response body safely
        # (If Nginx is still misconfigured, this will output HTML instead of JSON)
        if "application/json" in response.headers.get("Content-Type", ""):
            print("Success! JSON Response received:")
            print(response.json())
        else:
            print("Warning: Response is NOT JSON (It's returning HTML/SPA frontend):")
            print(response.text[:500])  # Prints the first 500 characters of the HTML

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")

if __name__ == "__main__":
    test_login()