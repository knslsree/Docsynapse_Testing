
import requests
import re
import json
from datetime import datetime

BASE_URL = "https://qadsapi.thelocal.co.in/dc"

# Test cases using deliberately malformed inputs
TEST_CASES = [
    {
        "name": "Invalid JSON",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": '{"invalid_json":'
    },
    {
        "name": "Unexpected JSON data types",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps({
            "name": ["unexpected", "array"],
            "id": {"invalid": "object"},
            "value": None
        })
    },
    {
        "name": "Empty JSON body",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": '{}'
    },
    {
        "name": "Invalid content type",
        "method": "POST",
        "headers": {"Content-Type": "text/plain"},
        "data": "DocSynapse security error test"
    },
    {
        "name": "Invalid HTTP method",
        "method": "TRACE",
        "headers": {},
        "data": None
    }
]

# Sensitive error disclosure indicators
PATTERNS = {
    "Python Stack Trace": r"Traceback \(most recent call last\)",
    "Java Exception": r"java\.(lang|io|sql)\.",
    "Dart Exception": r"(Unhandled Exception|Exception:)",
    "SQL Error": r"(SQL syntax|SQLSTATE|mysql_fetch|ORA-\d+)",
    "Internal File Path": r"(/var/www/|/home/|/usr/src/|[A-Za-z]:\\\\)",
    "Debug Information": r"(DEBUG\s*=\s*True|debug toolbar)",
    "Server Stack Trace": r"(at [\w.$]+\([\w.]+:\d+\)|Internal Server Error)",
    "Sensitive Credentials": r"(?i)(password|secret_key|access_token)\s*[:=]\s*['\"]?[^,\s'\"]+"
}

session = requests.Session()

session.headers.update({
    "User-Agent": "DocSynapse-Authorized-Security-Test/1.0",
    "Accept": "application/json"
})

results = []

print("=" * 70)
print("DOCSYNAPSE - ERROR HANDLING SECURITY TEST")
print("=" * 70)

for test in TEST_CASES:

    print(f"\nTesting: {test['name']}")

    try:
        response = session.request(
            method=test["method"],
            url=BASE_URL,
            headers=test["headers"],
            data=test["data"],
            timeout=15,
            allow_redirects=False
        )

        body = response.text
        findings = []

        print("HTTP Status:", response.status_code)

        for issue, pattern in PATTERNS.items():
            if re.search(pattern, body):
                findings.append(issue)

        if findings:
            status = "POTENTIAL INFORMATION DISCLOSURE"
            print("[WARNING]", status)

            for finding in findings:
                print(" -", finding)

        else:
            status = "No known disclosure pattern detected"
            print("[INFO]", status)

        results.append({
            "Test": test["name"],
            "HTTP Status": response.status_code,
            "Result": status,
            "Findings": findings
        })

    except requests.RequestException as error:
        print("[REQUEST ERROR]", str(error))

        results.append({
            "Test": test["name"],
            "HTTP Status": "N/A",
            "Result": "Request failed",
            "Findings": []
        })

# Save test report
filename = "DocSynapse_Error_Handling_Report.txt"

with open(filename, "w", encoding="utf-8") as report:
    report.write("DOCSYNAPSE ERROR HANDLING SECURITY REPORT\n")
    report.write("Date: " + datetime.now().isoformat() + "\n")
    report.write("Target: " + BASE_URL + "\n\n")

    for result in results:
        report.write(json.dumps(result, indent=4) + "\n\n")

print("\n" + "=" * 70)
print("TESTING COMPLETED")
print("Report saved:", filename)
print("=" * 70)
