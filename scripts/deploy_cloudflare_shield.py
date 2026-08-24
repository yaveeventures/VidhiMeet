import json
import os
import sys
import urllib.request
import urllib.error

ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "").strip()
TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()

if not ZONE_ID or not TOKEN:
    print("❌ Error: CLOUDFLARE_ZONE_ID and CLOUDFLARE_API_TOKEN environment variables must be set.")
    sys.exit(1)

BASE_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/rulesets"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def make_request(url, method="GET", payload=None):
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {"success": False, "errors": [{"message": body}], "status_code": e.code}

def deploy():
    print(f"[*] Connecting to Cloudflare API for Zone ID: {ZONE_ID}...")

    # 1. Get existing zone rulesets
    existing = make_request(BASE_URL)
    if not existing.get("success"):
        print(f"[X] Failed to fetch existing rulesets: {existing}")
        sys.exit(1)

    existing_phases = {}
    for rset in existing.get("result", []):
        existing_phases[rset.get("phase")] = rset.get("id")

    print(f"[*] Found existing ruleset phases: {list(existing_phases.keys())}")

    # --- Phase 1: Edge Rate Limiting ---
    ratelimit_payload = {
        "name": "VidhiMeet Auth Edge Rate Limiting",
        "kind": "zone",
        "phase": "http_ratelimit",
        "rules": [
            {
                "action": "block",
                "description": "Credential Stuffing & Auth Brute Force Protection",
                "expression": '(http.request.uri.path in {"/api/v1/auth/login" "/api/v1/auth/register" "/api/v1/auth/forgot-password" "/api/v1/auth/reset-password" "/api/v1/auth/google" "/admin-login.html"})',
                "enabled": True,
                "ratelimit": {
                    "characteristics": ["ip.src", "cf.colo.id"],
                    "period": 10,
                    "requests_per_period": 5,
                    "mitigation_timeout": 10
                }
            }
        ]
    }

    if "http_ratelimit" in existing_phases:
        rset_id = existing_phases["http_ratelimit"]
        print(f"[*] Updating existing http_ratelimit ruleset ({rset_id})...")
        res1 = make_request(f"{BASE_URL}/{rset_id}", method="PUT", payload=ratelimit_payload)
    else:
        print("[*] Creating new http_ratelimit ruleset...")
        res1 = make_request(BASE_URL, method="POST", payload=ratelimit_payload)

    if res1.get("success"):
        print("  [+] Layer 1: Edge Rate Limiting Rules Successfully Deployed!")
    else:
        print(f"  [!] Layer 1 Notice: {res1.get('errors')}")

    # --- Phase 2 & 3: Custom WAF & Bot Management ---
    waf_payload = {
        "name": "VidhiMeet Custom Edge WAF & Bot Shield",
        "kind": "zone",
        "phase": "http_request_firewall_custom",
        "rules": [
            # Rule 1: Known Recon Scanners & Bot Blocking
            {
                "action": "block",
                "description": "Block Known Malicious Scanners & Recon Bots",
                "expression": '(cf.client.bot or http.user_agent contains "nikto" or http.user_agent contains "sqlmap" or http.user_agent contains "nmap" or http.user_agent contains "dirbuster" or http.user_agent contains "gobuster" or http.user_agent contains "wpscan" or http.user_agent contains "masscan" or http.user_agent contains "python-requests" or http.user_agent contains "httpx" or http.user_agent contains "curl" or http.user_agent contains "wget")',
                "enabled": True
            },
            # Rule 2: Challenge Reconnaissance on API Docs & Directory
            {
                "action": "managed_challenge",
                "description": "Challenge Automated Access on API Docs & Admin Portal",
                "expression": '(http.request.uri.path in {"/docs" "/openapi.json" "/redoc" "/admin-login.html" "/admin.html"})',
                "enabled": True
            },
            # Rule 3: SQLi & XSS Edge Payload Shield
            {
                "action": "block",
                "description": "WAF Edge Shield: SQL Injection & XSS Payload Defense",
                "expression": '(http.request.uri.query contains "select" or http.request.uri.query contains "union" or http.request.uri.query contains "insert" or http.request.uri.query contains "delete" or http.request.uri.query contains "drop" or http.request.uri.query contains "<script" or http.request.uri.query contains "javascript:" or http.request.uri.query contains "onerror=" or http.request.full_uri contains "%27" or http.request.full_uri contains "%3Cscript")',
                "enabled": True
            },
            # Rule 4: Path Traversal & IDOR Enumeration Shield
            {
                "action": "block",
                "description": "WAF Edge Shield: Path Traversal, LFI & Account Enumeration Defense",
                "expression": '(http.request.uri.path contains "../" or http.request.uri.path contains "/etc/passwd" or http.request.uri.path contains "/win.ini" or http.request.uri.path contains "/proc/self" or http.request.uri.path contains ".env" or http.request.uri.path contains ".git" or http.request.uri.query contains "user_id[]" or http.request.uri.query contains "id[]")',
                "enabled": True
            }
        ]
    }

    if "http_request_firewall_custom" in existing_phases:
        rset_id = existing_phases["http_request_firewall_custom"]
        print(f"[*] Updating existing http_request_firewall_custom ruleset ({rset_id})...")
        res2 = make_request(f"{BASE_URL}/{rset_id}", method="PUT", payload=waf_payload)
    else:
        print("[*] Creating new http_request_firewall_custom ruleset...")
        res2 = make_request(BASE_URL, method="POST", payload=waf_payload)

    if res2.get("success"):
        print("  [+] Layers 2 & 3: WAF Payload & Bot Shield Rules Successfully Deployed!")
    else:
        print(f"  [!] Layers 2 & 3 Notice: {res2.get('errors')}")

    if res1.get("success") and res2.get("success"):
        print("\n[SUCCESS] Cloudflare Edge Firewall Shield is 100% DEPLOYED AND ACTIVE for VidhiMeet!")
    else:
        print("\n[PARTIAL/NOTICE] Review messages above.")

if __name__ == "__main__":
    deploy()
