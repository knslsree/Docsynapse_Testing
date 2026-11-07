
import dns.resolver
import dns.query
import dns.zone
import dns.exception
import csv
from datetime import datetime

# Replace with your authorized Dev domain
DOMAIN = "thelocal.co.in"

RECORD_TYPES = [
    "A",
    "AAAA",
    "MX",
    "NS",
    "TXT",
    "SOA",
    "CAA"
]

results = []

print("=" * 65)
print("DNS MISCONFIGURATION SECURITY TEST")
print("=" * 65)

print("Target domain:", DOMAIN)
print("Started:", datetime.now())
print("-" * 65)


def record_lookup(domain, record_type):

    try:
        answers = dns.resolver.resolve(
            domain,
            record_type,
            lifetime=5
        )

        for answer in answers:
            value = str(answer)

            print(f"[FOUND] {record_type}: {value}")

            results.append([
                domain,
                record_type,
                value,
                "FOUND"
            ])

        return answers

    except dns.resolver.NoAnswer:
        print(f"[INFO] No {record_type} record")

    except dns.resolver.NXDOMAIN:
        print("[ERROR] Domain does not exist")

    except dns.exception.Timeout:
        print(f"[WARNING] {record_type} lookup timed out")

    except Exception as error:
        print(f"[ERROR] {record_type}: {error}")

    return None


# 1. DNS record enumeration
print("\n[1] DNS RECORD DISCOVERY")

for record_type in RECORD_TYPES:
    record_lookup(DOMAIN, record_type)


# 2. SPF validation
print("\n[2] SPF CONFIGURATION CHECK")

txt_records = record_lookup(DOMAIN, "TXT")

spf_found = False

if txt_records:
    for record in txt_records:
        value = str(record).strip('"')

        if value.lower().startswith("v=spf1"):
            spf_found = True
            print("[FOUND] SPF record:", value)

if not spf_found:
    print("[WARNING] SPF record not identified")


# 3. DMARC validation
print("\n[3] DMARC CONFIGURATION CHECK")

dmarc_domain = "_dmarc." + DOMAIN

dmarc_records = record_lookup(dmarc_domain, "TXT")

if not dmarc_records:
    print("[WARNING] DMARC record not identified")


# 4. DNSSEC validation
print("\n[4] DNSSEC CHECK")

dnskey_records = record_lookup(DOMAIN, "DNSKEY")

if dnskey_records:
    print("[INFO] DNSKEY records exist.")
else:
    print("[INFO] No DNSKEY records found.")
    print("[INFO] Verify DNSSEC signing and DS records with the DNS provider.")


# 5. DNS Zone Transfer check
print("\n[5] DNS ZONE TRANSFER CHECK")

ns_records = record_lookup(DOMAIN, "NS")

if ns_records:

    for ns in ns_records:

        nameserver = str(ns).rstrip(".")

        try:
            transfer = dns.query.xfr(
                nameserver,
                DOMAIN,
                timeout=5,
                lifetime=10
            )

            zone = dns.zone.from_xfr(transfer)

            if zone:
                print("[CRITICAL] DNS ZONE TRANSFER POSSIBLE!")
                print("Nameserver:", nameserver)

                results.append([
                    DOMAIN,
                    "AXFR",
                    nameserver,
                    "POTENTIAL EXPOSURE"
                ])

        except Exception:
            print("[PASS] Zone transfer not permitted:",
                  nameserver)

            results.append([
                DOMAIN,
                "AXFR",
                nameserver,
                "NOT PERMITTED / NOT VERIFIED"
            ])


# 6. Export results
filename = "dns_security_results.csv"

with open(filename, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Domain",
        "DNS Record",
        "Value",
        "Finding"
    ])

    writer.writerows(results)


print("\n" + "=" * 65)
print("DNS SECURITY TEST COMPLETED")
print("=" * 65)

print("Domain:", DOMAIN)
print("Total findings:", len(results))
print("Report:", filename)
print("Completed:", datetime.now())
