https://dsapi.thelocal.co.in/dc/api/v1/auth/login
import requests
import json
import csv
import time
import os
from datetime import datetime

# ==========================================
# DOCSYNAPSE MALICIOUS INPUT SECURITY TEST
# ==========================================

print("=" * 65)
print("DOCSYNAPSE - MALICIOUS INPUT SECURITY TESTING")
print("=" * 65)

# Enter an authorized DEV/UAT API endpoint
URL = input("Enter DocSynapse API endpoint: ").strip()

# Example: https://dsapi.thelocal.co.in/dc/your-endpoint

if not URL.startswith("https://"):
    raise ValueError("Use an authorized HTTPS testing endpoint.")

FIELD = input("Enter the JSON field to test (e.g. name): ").strip()

if not FIELD:
    raise ValueError("Field name cannot be empty.")

# Optional bearer token from environment variable
TOKEN = os.getenv("DOCSYNAPSE_TOKEN", "")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# ==========================================
# MALICIOUS / UNEXPECTED TEST INPUTS
# ==========================================

TEST_CASES = [
    ("SQL Injection", "' OR '1'='1"),
    ("SQL Injection", "admin'--"),
    ("SQL Injection", "1 UNION SELECT NULL--"),

    ("XSS", "<script>alert(1)</script>"),
    ("XSS", "<img src=x onerror=alert(1)>"),
    ("HTML Injection", "<h1>SecurityTest</h1>"),

    ("Command Injection", "; whoami"),
    ("Command Injection", "$(whoami)"),

    ("Path Traversal", "../../etc/passwd"),
    ("Path Traversal", "..\\..\\windows\\win.ini"),

    ("SSTI", "{{7*7}}"),
    ("SSTI", "${7*7}"),

    ("NoSQL Injection", {"$ne": None}),
    ("NoSQL Injection", {"$gt": ""}),

    ("XML Injection", "<test><value>123</value></test>"),
    ("Null Byte", "test\\x00value"),

    ("Special Characters", "!@#$%^&*()_+-=[]{}|;':,./<>?"),
    ("Unicode Input", "测试安全🚀"),
    ("Empty Input", ""),
    ("Whitespace Input", "     "),
    ("Numeric Input", 999999999999999999),
    ("Negative Number", -999999),
    ("Boolean Input", True),
    ("JSON Type Manipulation", ["admin", "user"]),
    ("Oversized Input", "A" * 10000)
]

# ==========================================
# EXECUTE TESTS
# ==========================================

results = []

for number, (category, payload) in enumerate(TEST_CASES, start=1):

    print(f"\n[{number}/{len(TEST_CASES)}] Testing: {category}")

    body = {FIELD: payload}

    try:
        start = time.perf_counter()

        response = requests.post(
            URL,
            headers=HEADERS,
            json=body,
            timeout=15,
            allow_redirects=False
        )

        elapsed = round(time.perf_counter() - start, 3)

        status = response.status_code
        response_text = response.text[:3000].lower()

        # Basic response observations
        if status in [200, 201, 202]:
            observation = "Request accepted - inspect validation and stored output"
        elif status in [400, 401, 403, 413, 415, 422]:
            observation = "Request rejected or restricted"
        elif status >= 500:
            observation = "Server error - investigate possible input handling failure"
        else:
            observation = "Review response manually"

        # Check whether submitted XSS text is reflected
        if category == "XSS":
            if "<script>" in response_text or "onerror=alert(1)" in response_text:
                observation += " | Potential unescaped reflection"

        # Check for common database error disclosure
        error_indicators = [
            "sql syntax",
            "mysql error",
            "sqlite error",
            "postgresql error",
            "traceback",
            "syntaxerror"
        ]

        if any(item in response_text for item in error_indicators):
            observation += " | Possible internal error disclosure"

        print("HTTP Status:", status)
        print("Response Time:", elapsed, "seconds")
        print("Observation:", observation)

        results.append({
            "Test No": number,
            "Category": category,
            "Payload": str(payload)[:200],
            "HTTP Status": status,
            "Response Time": elapsed,
            "Observation": observation
        })

    except requests.exceptions.Timeout:
        print("TIMEOUT - investigate server response")
        results.append({
            "Test No": number,
            "Category": category,
            "Payload": str(payload)[:200],
            "HTTP Status": "TIMEOUT",
            "Response Time": "",
            "Observation": "Request timed out; investigate"
        })

    except requests.exceptions.RequestException as error:
        print("REQUEST ERROR:", str(error))
        results.append({
            "Test No": number,
            "Category": category,
            "Payload": str(payload)[:200],
            "HTTP Status": "ERROR",
            "Response Time": "",
            "Observation": "Request failed"
        })

    time.sleep(0.3)

# ==========================================
# EXPORT RESULTS
# ==========================================

filename = "DocSynapse_Malicious_Input_Report.csv"

with open(filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Test No",
            "Category",
            "Payload",
            "HTTP Status",
            "Response Time",
            "Observation"
        ]
    )

    writer.writeheader()
    writer.writerows(results)

print("\n" + "=" * 65)
print("DOCSYNAPSE SECURITY TEST COMPLETED")
print("=" * 65)
print("Total Tests:", len(results))
print("Report:", filename)
