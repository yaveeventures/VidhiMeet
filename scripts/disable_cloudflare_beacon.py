#!/usr/bin/env python3
"""
VidhiMeet Cloudflare Web Analytics (beacon.min.js) Disabler
Disables automatic injection of beacon.min.js / RUM to resolve
Lighthouse 'Legacy JavaScript' and 'Efficient Cache Lifetimes' audits.
"""

import os
import sys
import json
import urllib.request
import urllib.error

TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()

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

def main():
    if not TOKEN:
        print("❌ Error: CLOUDFLARE_API_TOKEN environment variable must be set.")
        sys.exit(1)

    account_id = ACCOUNT_ID
    if not account_id:
        # Fetch accounts associated with this token
        print("[*] Fetching Cloudflare Account ID...")
        acc_resp = make_request("https://api.cloudflare.com/client/v4/accounts")
        if acc_resp.get("success") and acc_resp.get("result"):
            account_id = acc_resp["result"][0]["id"]
            print(f"[+] Found Account ID: {account_id}")
        else:
            print("❌ Error: Could not determine Account ID. Set CLOUDFLARE_ACCOUNT_ID.")
            sys.exit(1)

    # 1. Fetch RUM sites
    rum_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/rum/site_info"
    print(f"[*] Fetching Web Analytics RUM sites for account {account_id}...")
    rum_resp = make_request(rum_url)

    if not rum_resp.get("success"):
        print(f"❌ Failed to fetch RUM sites: {rum_resp.get('errors')}")
        sys.exit(1)

    sites = rum_resp.get("result", [])
    if not sites:
        print("[i] No active Web Analytics RUM sites found on this account.")
        return

    for site in sites:
        site_tag = site.get("site_tag") or site.get("id")
        host = site.get("host", "unknown")
        auto_install = site.get("auto_install", False)
        print(f"\nSite: {host} (Tag: {site_tag}) | Auto-Install: {auto_install}")

        if auto_install or site.get("enabled", True):
            print(f"[*] Disabling automatic beacon injection for {host}...")
            update_url = f"{rum_url}/{site_tag}"
            patch_payload = {
                "auto_install": False,
                "enabled": False
            }
            res = make_request(update_url, method="PUT", payload=patch_payload)
            if res.get("success"):
                print(f"  [+] Successfully disabled automatic beacon.min.js injection for {host}!")
            else:
                print(f"  [!] Notice: {res.get('errors')}")

    print("\n[SUCCESS] Remember to purge Cloudflare cache ('Purge Everything') so edge nodes serve clean HTML.")

if __name__ == "__main__":
    main()
