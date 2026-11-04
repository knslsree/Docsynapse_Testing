import requests

# Replace with your website or local app URL (e.g., http://127.0.0.1:5000)
url = "https://dsapi.thelocal.co.in/dc/api/v1/auth/login"

try:
    response = requests.get(url)
    headers = response.headers

    print(f"--- Checking Security Headers for: {url} ---\n")

    # 1. Check Content-Security-Policy (The most important defense)
    csp = headers.get("Content-Security-Policy")
    if csp:
        print("[PASS] Content-Security-Policy is present:")
        print(f"       {csp}\n")
    else:
        print("[FAIL] Content-Security-Policy header is MISSING! (High Risk)\n")

    # 2. Check X-XSS-Protection
    xss_protection = headers.get("X-XSS-Protection")
    if xss_protection == "0":
        print("[PASS] X-XSS-Protection is set to '0' (Modern Best Practice - CSP is used instead).")
    elif xss_protection == "1; mode=block":
        print("[INFO] X-XSS-Protection is set to '1; mode=block' (Legacy browser protection enabled).")
    else:
        print(f"[WARN] X-XSS-Protection header value is: '{xss_protection}'")

    # 3. Check X-Content-Type-Options (Prevents MIME-sniffing XSS)
    nosniff = headers.get("X-Content-Type-Options")
    if nosniff == "nosniff":
        print("[PASS] X-Content-Type-Options: nosniff is set correctly.")
    else:
        print("[FAIL] X-Content-Type-Options: nosniff is missing.")

except requests.exceptions.RequestException as e:
    print(f"Could not connect to {url}. Error: {e}")