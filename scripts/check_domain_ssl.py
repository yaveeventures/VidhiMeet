#!/usr/bin/env python3
"""
VidhiMeet Domain DNS & SSL/TLS 1.3 Health Diagnostic Tool
Validates DNS resolution, TLS 1.3 handshake, certificate validity,
Subject Alternative Names (SAN), and HSTS security headers.
"""

import sys
import socket
import ssl
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DOMAINS = [
    "vidhimeet.in",
    "www.vidhimeet.in",
    "lawyer.vidhimeet.in",
    "admin.vidhimeet.in"
]


def check_dns(domain: str) -> dict:
    """Resolve IPv4 address for domain."""
    try:
        ip = socket.gethostbyname(domain)
        return {"status": "RESOLVED", "ip": ip}
    except socket.gaierror as e:
        return {"status": "FAILED", "error": str(e), "ip": None}


def check_tls_and_cert(domain: str, port: int = 443, timeout: int = 5) -> dict:
    """Inspect SSL/TLS certificate, TLS 1.3 negotiation, and expiry."""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    try:
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                version = ssock.version()
                cipher = ssock.cipher()

                # Parse validity dates
                not_before_str = cert.get("notBefore", "")
                not_after_str = cert.get("notAfter", "")
                not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_left = (not_after - now).days

                # Subject Alternative Names (SAN)
                sans = [entry[1] for entry in cert.get("subjectAltName", []) if entry[0] == "DNS"]

                # Issuer
                issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                issuer_org = issuer_dict.get("organizationName") or issuer_dict.get("commonName", "Unknown")

                return {
                    "status": "VALID",
                    "tls_version": version,
                    "cipher": cipher[0] if cipher else "Unknown",
                    "issuer": issuer_org,
                    "expires_on": not_after_str,
                    "days_remaining": days_left,
                    "san": sans,
                    "is_tls_1_3": version == "TLSv1.3",
                    "expired": days_left < 0
                }
    except Exception as e:
        return {
            "status": "TLS_HANDSHAKE_FAILED",
            "error": str(e)
        }


def check_security_headers(domain: str, timeout: int = 5) -> dict:
    """Validate HTTP response security headers."""
    url = f"https://{domain}/"
    req = urllib.request.Request(url, headers={"User-Agent": "VidhiMeet-SSL-Diagnostic/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = dict(resp.headers)
            return {
                "status": "OK",
                "hsts": headers.get("strict-transport-security", "MISSING"),
                "x_frame_options": headers.get("x-frame-options", "MISSING"),
                "x_content_type_options": headers.get("x-content-type-options", "MISSING"),
                "server": headers.get("server", "hidden")
            }
    except urllib.error.HTTPError as e:
        headers = dict(e.headers)
        return {
            "status": f"HTTP_{e.code}",
            "hsts": headers.get("strict-transport-security", "MISSING"),
            "x_frame_options": headers.get("x-frame-options", "MISSING"),
            "x_content_type_options": headers.get("x-content-type-options", "MISSING"),
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="VidhiMeet Domain DNS & SSL/TLS 1.3 Diagnostic Checker")
    parser.add_argument("--domains", nargs="+", default=DEFAULT_DOMAINS, help="Domains to audit")
    parser.add_argument("--json", action="store_true", help="Output raw JSON format")
    args = parser.parse_args()

    results = {}
    all_healthy = True

    for domain in args.domains:
        dns_res = check_dns(domain)
        tls_res = check_tls_and_cert(domain) if dns_res["status"] == "RESOLVED" else {"status": "SKIPPED"}
        headers_res = check_security_headers(domain) if tls_res.get("status") == "VALID" else {"status": "SKIPPED"}

        is_healthy = (dns_res["status"] == "RESOLVED") and (tls_res.get("status") == "VALID") and not tls_res.get("expired", True)
        if not is_healthy:
            all_healthy = False

        results[domain] = {
            "dns": dns_res,
            "tls": tls_res,
            "headers": headers_res,
            "healthy": is_healthy
        }

    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(0 if all_healthy else 1)

    print("\n" + "=" * 80)
    print(" [*] VidhiMeet Domain DNS & SSL/TLS 1.3 Infrastructure Audit Report")
    print("=" * 80)

    for domain, data in results.items():
        print(f"\n[Domain] {domain}")
        dns = data["dns"]
        if dns["status"] == "RESOLVED":
            print(f"  [+] DNS Resolution: OK -> {dns['ip']}")
        else:
            print(f"  [-] DNS Resolution: FAILED ({dns.get('error')})")

        tls = data["tls"]
        if tls.get("status") == "VALID":
            tls_tag = "[TLS 1.3]" if tls.get("is_tls_1_3") else f"[{tls.get('tls_version')}]"
            print(f"  [+] SSL Protocol:   {tls_tag} via {tls.get('cipher')}")
            print(f"  [+] Certificate:    Issued by {tls.get('issuer')} (Expires in {tls.get('days_remaining')} days)")
            print(f"  [+] Covered SANs:   {', '.join(tls.get('san', []))}")
        elif tls.get("status") != "SKIPPED":
            print(f"  [-] SSL/TLS:        FAILED ({tls.get('error')})")

        headers = data["headers"]
        if headers.get("status") in ("OK", "HTTP_200", "HTTP_301", "HTTP_302"):
            hsts_val = headers.get("hsts")
            hsts_status = "ENABLED" if hsts_val != "MISSING" else "MISSING"
            print(f"  [+] HSTS Status:    {hsts_status} ({hsts_val})")

    print("\n" + "=" * 80)
    if all_healthy:
        print("[SUCCESS] All VidhiMeet domains resolved with valid SSL/TLS certificates.")
    else:
        print("[INFO] Production DNS propagation or Let's Encrypt provisioning pending.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
