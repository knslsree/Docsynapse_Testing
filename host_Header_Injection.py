
import requests
import json
import re
from datetime import datetime
from urllib.parse import urlparse

BASE_URL = "https://qadsapi.thelocal.co.in/dc"
TIMEOUT = 15

session = requests.Session()
session.headers.update({
    "User-Agent": "DocSynapse-Advanced-Security-Test/1.0",
    "Accept": "application/json"
})

results = []

def save_result(test, status, details):
    results.append({
        "test": test,
        "status": status,
        "details": details
    })
    print(f"[{status}] {test}: {details}")


def inspect_response(test, response, markers):
    content = response.text[:30000]
    locations = response.headers.get("Location", "")
    combined = content + locations

    matches = [m for m in markers if m.lower() in combined.lower()]

    if matches:
        save_result(
            test,
            "REVIEW",
            f"Unexpected marker reflection: {matches}; "
            f"HTTP {response.status_code}"
        )
    else:
        save_result(
            test,
            "REVIEW",
            f"No marker reflection detected; HTTP {response.status_code}"
        )


print("=" * 65)
print("DOCSYNAPSE ADVANCED SERVER SECURITY TEST")
print("=" * 65)


# TEST 1: Host Header Injection
print("\nTEST 1: Host Header Injection")

host_tests = [
    {
        "Host": "attacker.invalid"
    },
    {
        "X-Forwarded-Host": "attacker.invalid"
    },
    {
        "X-Original-Host": "attacker.invalid"
    },
    {
        "Forwarded": "host=attacker.invalid"
    }
]

for headers in host_tests:
    try:
        response = session.get(
            BASE_URL,
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=False
        )

        inspect_response(
            "Host Header / Proxy Header Trust",
            response,
            ["attacker.invalid"]
        )

        print("Headers tested:", headers)
        print("Response Location:",
              response.headers.get("Location", "None"))

    except requests.RequestException as error:
        save_result("Host Header Injection", "ERROR", str(error))


# TEST 2: HTTP Parameter Pollution
print("\nTEST 2: HTTP Parameter Pollution")

parameter_tests = [
    [("test", "first"), ("test", "second")],
    [("page", "1"), ("page", "999999")],
    [("limit", "10"), ("limit", "1000000")],
    [("sort", "asc"), ("sort", "desc")]
]

for params in parameter_tests:
    try:
        response = session.get(
            BASE_URL,
            params=params,
            timeout=TIMEOUT,
            allow_redirects=False
        )

        save_result(
            "HTTP Parameter Pollution",
            "REVIEW",
            f"Parameters: {params}; HTTP {response.status_code}; "
            f"Response size: {len(response.content)} bytes"
        )

    except requests.RequestException as error:
        save_result("HTTP Parameter Pollution", "ERROR", str(error))


# TEST 3: Path Normalization
print("\nTEST 3: Path Normalization")

parsed = urlparse(BASE_URL)
origin = f"{parsed.scheme}://{parsed.netloc}"

path_tests = [
    "/dc/",
    "/dc/.",
    "/dc/..",
    "/dc/%2e",
    "/dc/%2e%2e",
    "/dc/%252e%252e"
]

for path in path_tests:
    try:
        response = session.get(
            origin + path,
            timeout=TIMEOUT,
            allow_redirects=False
        )

        save_result(
            "Path Normalization",
            "REVIEW",
            f"Path: {path}; HTTP {response.status_code}; "
            f"Length: {len(response.content)}"
        )

    except requests.RequestException as error:
        save_result("Path Normalization", "ERROR", str(error))


# TEST 4: Cache-Control Validation
print("\nTEST 4: Cache-Control Validation")

cache_tests = [
    {"Cache-Control": "no-cache"},
    {"Cache-Control": "no-store"},
    {"Pragma": "no-cache"}
]

for headers in cache_tests:
    try:
        response = session.get(
            BASE_URL,
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=False
        )

        cache_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() in [
                "cache-control",
                "pragma",
                "expires",
                "age",
                "vary",
                "etag",
                "x-cache",
                "cf-cache-status"
            ]
        }

        save_result(
            "Cache-Control Validation",
            "REVIEW",
            json.dumps(cache_headers)
        )

    except requests.RequestException as error:
        save_result("Cache-Control Validation", "ERROR", str(error))


# TEST 5: Response Security Metadata
print("\nTEST 5: Response Metadata")

try:
    response = session.get(
        BASE_URL,
        timeout=TIMEOUT,
        allow_redirects=False
    )

    metadata = {
        "status": response.status_code,
        "content_type": response.headers.get("Content-Type"),
        "content_length": response.headers.get("Content-Length"),
        "cache_control": response.headers.get("Cache-Control"),
        "vary": response.headers.get("Vary"),
        "request_id": response.headers.get("X-Request-ID")
    }

    save_result(
        "Response Metadata Inspection",
        "REVIEW",
        json.dumps(metadata)
    )

except requests.RequestException as error:
    save_result("Response Metadata Inspection", "ERROR", str(error))


# REPORT
report = {
    "application": "DocSynapse",
    "target": BASE_URL,
    "date": datetime.now().isoformat(),
    "test_suite": "Advanced Server-Side Security",
    "total_tests": len(results),
    "results": results
}

with open(
    "DocSynapse_Advanced_Server_Security.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(report, file, indent=4)

print("\n" + "=" * 65)
print("ADVANCED TESTING COMPLETED")
print("Total checks:", len(results))
print("Report: DocSynapse_Advanced_Server_Security.json")
print("=" * 65)
