import sys
import requests

# Base URLs configured for DocSynapse environment
LOGIN_URL = "https://devdocsynapse.thelocal.co.in"
API_BASE = "https://dsapi.thelocal.co.in/dc/api/v1"

def test_cors_misconfiguration(target_url):
    # List of malicious/unauthorized test origins to simulate cross-origin attacks
    test_origins = [
        "https://evil-attacker.com",
        "null",
        "https://devdocsynapse.thelocal.co.in.evil-attacker.com",  # Subdomain prefix bypass attempt
        "http://localhost:3000"                                    # Untrusted local origin
    ]
    
    print(f"[*] Starting CORS Misconfiguration Scan on target: {target_url}\n")
    
    for origin in test_origins:
        headers = {
            "Origin": origin,
            "User-Agent": "Mozilla/5.0 (DocSynapse-CORS-Tester)"
        }
        
        try:
            response = requests.get(target_url, headers=headers, timeout=5)
            
            acao = response.headers.get("Access-Control-Allow-Origin")
            acac = response.headers.get("Access-Control-Allow-Credentials")
            
            print(f"[->] Testing Origin: {origin}")
            print(f"     Access-Control-Allow-Origin: {acao}")
            print(f"     Access-Control-Allow-Credentials: {acac}")
            
            if acao == origin:
                if acac and acac.lower() == 'true':
                    print("     [!] VULNERABLE: Dynamic origin reflection with credentials enabled (High Risk)")
                else:
                    print("     [!] POTENTIALLY VULNERABLE: Dynamic origin reflection without credentials (Medium Risk)")
            elif acao == "*":
                print("     [!] WARNING: Wildcard '*' returned.")
            else:
                print("     [-] SECURE: Origin properly rejected or suppressed.")
            print("-" * 65)
            
        except requests.exceptions.RequestException as e:
            print(f"[-] Connection error to target ({target_url}): {e}\n")

if __name__ == "__main__":
    # Test configured endpoints
    endpoints = [
        f"{LOGIN_URL}/login",
        f"{API_BASE}/patient-data"
    ]
    
    for ep in endpoints:
        test_cors_misconfiguration(ep)