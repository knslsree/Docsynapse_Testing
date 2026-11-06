#!/usr/bin/env python3
"""
Robust TLS Protocol & Weak Cipher Command-Line Auditor
Usage: python tls_audit.py <hostname> [port]
"""

import argparse
import socket
import ssl
import sys

def test_protocol(hostname, port, min_v, max_v, proto_name):
    """Tests if a specific TLS version is supported by the target."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        context.minimum_version = min_v
        context.maximum_version = max_v
    except (ValueError, AttributeError) as e:
        return False, f"Blocked or unsupported by local runtime/OpenSSL ({e})"

    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cipher = ssock.cipher()
                version = ssock.version()
                return True, f"Supported | Active Protocol: {version} | Cipher: {cipher[0]}"
    except ssl.SSLError as e:
        return False, f"Rejected / Disabled (Handshake failed: {getattr(e, 'reason', e)})"
    except socket.timeout:
        return False, "Connection timed out"
    except Exception as e:
        return False, f"Connection failed: {e}"

def check_weak_ciphers(hostname, port):
    """Checks if the server negotiates common vulnerable or deprecated ciphers."""
    weak_ciphers = [
        "RC4-SHA",
        "RC4-MD5",
        "DES-CBC3-SHA",
        "EDH-RSA-DES-CBC3-SHA",
        "ECDHE-RSA-DES-CBC3-SHA"
    ]
    accepted = []
    for cipher in weak_ciphers:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers(cipher)
        except (ssl.SSLError, ValueError):
            # Local OpenSSL build doesn't even recognize or allow setting this cipher
            continue
            
        try:
            with socket.create_connection((hostname, port), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    accepted.append(cipher)
        except Exception:
            pass
    return accepted

def main():
    parser = argparse.ArgumentParser(description="Audit a target host for TLS version compliance and weak ciphers.")
    parser.add_argument("host", help="Target hostname or IP address (e.g., scanme.nmap.org)")
    parser.add_argument("port", nargs="?", type=int, default=443, help="Target port (default: 443)")
    args = parser.parse_args()

    print(f"\n[+] Initializing TLS Audit for target: {args.host}:{args.port}\n")

    protocols = [
        ("TLS 1.0", ssl.TLSVersion.TLSv1, ssl.TLSVersion.TLSv1),
        ("TLS 1.1", ssl.TLSVersion.TLSv1_1, ssl.TLSVersion.TLSv1_1),
        ("TLS 1.2", ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2),
        ("TLS 1.3", ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_3),
    ]

    print("--- Protocol Support Audit ---")
    for name, min_v, max_v in protocols:
        supported, details = test_protocol(args.host, args.port, min_v, max_v, name)
        status = "SECURE / DISABLED" if (name in ["TLS 1.0", "TLS 1.1"] and not supported) else ("SUPPORTED" if supported else "NOT SUPPORTED")
        print(f"  {name:<10} -> [{status}] {details}")

    print("\n--- Weak Cipher Audit ---")
    weak_found = check_weak_ciphers(args.host, args.port)
    if weak_found:
        print("  [!] VULNERABILITY DETECTED: Server accepted weak/deprecated ciphers:")
        for c in weak_found:
            print(f"      - {c}")
    else:
        print("  [+] PASS: No tested legacy/weak ciphers were successfully negotiated.")
    
    print("\n[+] Audit execution completed successfully.\n")

if __name__ == "__main__":
    main()