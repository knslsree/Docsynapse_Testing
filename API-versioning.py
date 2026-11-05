import requests

# Disable SSL warnings for self-signed certificates in dev environments
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

# Configured Endpoints
API_BASE = "https://dsapi.thelocal.co.in" + "/dc/api/v1"
LOGIN_URL = "https://devdocsynapse.thelocal.co.in"


def test_api_governance():
  print("=" * 60)
  print("[1] Testing API Versioning & Disclosure")
  print("=" * 60)

  # Test Valid Version
  valid_url = f"{API_BASE}/patient-data"
  try:
    print(f"-> Testing valid endpoint: {valid_url}")
    res = requests.get(valid_url, verify=False, timeout=10)
    print(f"   Status Code: {res.status_code}")
  except Exception as e:
    print(f"   Error: {e}")

  # Test Invalid Version (v99)
  invalid_url = "https://dsapi.thelocal.co.in/dc/api/v99/patient-data"
  try:
    print(f"-> Testing invalid version endpoint: {invalid_url}")
    res = requests.get(invalid_url, verify=False, timeout=10)
    print(f"   Status Code: {res.status_code} (Expected 404/400)")
  except Exception as e:
    print(f"   Error: {e}")

  # Test Header Disclosure
  try:
    print(f"-> Inspecting response headers for disclosure: {API_BASE}")
    res = requests.get(API_BASE, verify=False, timeout=10)
    for header in ["Server", "X-Powered-By", "X-AspNet-Version"]:
      val = res.headers.get(header)
      if val:
        print(f"   [WARNING] Header '{header}': '{val}'")
      else:
        print(f"   [PASS] Header '{header}' is hidden.")
  except Exception as e:
    print(f"   Error: {e}")


def test_auth_and_cors():
  print("\n" + "=" * 60)
  print("[2] Testing Login, Token, and Rate Limiting")
  print("=" * 60)

  login_endpoint = f"{LOGIN_URL}/login"
  payload = {"username": "admin", "password": "securepassword123"}

  # Test Login
  token = None
  try:
    print(f"-> Attempting login at: {login_endpoint}")
    res = requests.post(login_endpoint, json=payload, verify=False, timeout=10)
    if res.status_code == 200:
      data = res.json()
      token = data.get("token")
      print(f"   [PASS] Login successful. Token acquired: {token}")
    else:
      print(f"   [FAIL] Login returned status {res.status_code}: {res.text}")
  except Exception as e:
    print(f"   [ERROR] Login request failed: {e}")

  # Test Rate Limiting on Login
  print("-> Triggering rapid requests for Rate Limiting test...")
  for i in range(1, 7):
    try:
      r = requests.post(login_endpoint, json=payload, verify=False, timeout=5)
      if r.status_code == 429:
        print(
            f"   Request {i}: HTTP 429 Too Many Requests (Rate limit active!"
            " [PASS])"
        )
        break
      else:
        print(f"   Request {i}: Status {r.status_code}")
    except Exception:
      pass


if __name__ == "__main__":
  test_api_governance()
  test_auth_and_cors()