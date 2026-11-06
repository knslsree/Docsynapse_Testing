import requests
from bs4 import BeautifulSoup

def access_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

        print("Status Code:", response.status_code)
        print("Final URL:", response.url)

        if response.status_code == 200:
            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            with open(
                "page_content.html",
                "w",
                encoding="utf-8"
            ) as file:
                file.write(soup.prettify())

            print("Page saved successfully.")

        elif response.status_code == 401:
            print("Authentication required.")

        elif response.status_code == 403:
            print("Access forbidden.")

        elif response.status_code == 404:
            print("Page not found.")

        else:
            print("HTTP Status:", response.status_code)

    except requests.exceptions.Timeout:
        print("Request timed out.")

    except requests.exceptions.RequestException as error:
        print("Connection error:", error)


if __name__ == "__main__":
    target_url = input("Enter URL: ")
    access_url(target_url)