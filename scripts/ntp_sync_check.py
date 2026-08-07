"""
ntp_sync_check.py
-----------------
CERT-In / DPDP NTP Compliance — Standalone clock drift check script.

Run this as a cron job (every 15 minutes recommended) on every server that
hosts the application, database, or payment gateway to ensure clocks stay
aligned with Indian government NTP sources (NPL / NIC).

Usage:
    python -m scripts.ntp_sync_check              # standard check
    python -m scripts.ntp_sync_check --all        # query ALL servers, don't stop at first
    python -m scripts.ntp_sync_check --json       # machine-readable JSON output
    python -m scripts.ntp_sync_check --threshold 1.0  # custom drift threshold (seconds)

Exit codes:
    0  — All servers within tolerance
    1  — Drift exceeded threshold (or all servers unreachable)

Cron example (every 15 minutes, structured logs to syslog):
    */15 * * * * /usr/bin/python3 -m scripts.ntp_sync_check --json 2>&1 | logger -t ntp_compliance
"""

import argparse
import json
import logging
import os
import socket
import struct
import sys
from datetime import datetime, timedelta, timezone

# ── Bootstrap path ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── NTP Constants (RFC 5905) ───────────────────────────────────────────────────
_NTP_PORT = 123
_NTP_DELTA = 2208988800   # Seconds between NTP epoch (1900) and Unix epoch (1970)
_NTP_PACKET = b"\x1b" + 47 * b"\0"  # LI=0, VN=3, Mode=3 (client)
_NTP_PACKET_FORMAT = "!B B b b 11I"

# ── Default NPL / NIC server list ─────────────────────────────────────────────
_DEFAULT_SERVERS = [
    ("time.nplindia.org",  "National Physical Laboratory (NPL) — Primary"),
    ("time.nplindia.in",   "National Physical Laboratory (NPL) — Secondary"),
    ("time.nic.in",        "National Informatics Centre (NIC) — Tertiary"),
    ("pool.ntp.org",       "NTP Pool Project — Last-resort fallback"),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("ntp_sync_check")


def _query_server(host: str, timeout: float) -> dict:
    """Query a single NTP server, return structured result dict."""
    result = {
        "server": host,
        "reachable": False,
        "ntp_time": None,
        "drift_seconds": None,
        "error": None,
    }
    system_time = datetime.now(timezone.utc)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(_NTP_PACKET, (host, _NTP_PORT))
            data, _ = sock.recvfrom(48)
        if len(data) < 48:
            result["error"] = "Response too short"
            return result
        unpacked = struct.unpack(_NTP_PACKET_FORMAT, data)
        tx_sec = unpacked[10] - _NTP_DELTA
        tx_frac = unpacked[11]
        ntp_dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
            seconds=tx_sec, microseconds=tx_frac * 1_000_000 / (2 ** 32)
        )
        drift = (system_time - ntp_dt).total_seconds()
        result.update({
            "reachable": True,
            "ntp_time": ntp_dt.isoformat(),
            "system_time": system_time.isoformat(),
            "drift_seconds": round(drift, 6),
        })
    except socket.timeout:
        result["error"] = "Timeout"
    except Exception as exc:
        result["error"] = str(exc)
    return result


def run_check(servers: list[tuple[str, str]], timeout: float, threshold: float,
              query_all: bool, json_output: bool) -> int:
    """
    Run NTP drift checks. Returns 0 on success, 1 on failure.
    """
    results = []
    synced = False
    checked_at = datetime.now(timezone.utc).isoformat()

    for host, description in servers:
        r = _query_server(host, timeout)
        r["description"] = description
        r["within_tolerance"] = (
            abs(r["drift_seconds"]) <= threshold if r["drift_seconds"] is not None else False
        )
        results.append(r)

        if not query_all and r["reachable"]:
            # Found a working server — stop after first success (like ntp_now())
            if r["within_tolerance"]:
                synced = True
            break

    if query_all:
        synced = any(r["within_tolerance"] for r in results if r["reachable"])

    summary = {
        "checked_at": checked_at,
        "threshold_seconds": threshold,
        "overall_status": "OK" if synced else "ALERT",
        "results": results,
    }

    if json_output:
        print(json.dumps(summary, indent=2))
    else:
        _print_human(summary)

    return 0 if synced else 1


def _print_human(summary: dict):
    status_icon = "✅" if summary["overall_status"] == "OK" else "❌"
    print(f"\n{status_icon}  NTP Compliance Check — {summary['checked_at']}")
    print(f"   Drift threshold: ±{summary['threshold_seconds']}s\n")
    for r in summary["results"]:
        reachable_icon = "🟢" if r["reachable"] else "🔴"
        desc = r.get("description", "")
        if r["reachable"]:
            tol = "✅ within tolerance" if r["within_tolerance"] else f"⚠️  DRIFT ALERT"
            print(f"   {reachable_icon} {r['server']:30s}  drift={r['drift_seconds']:+.3f}s  {tol}")
            print(f"      └─ {desc}")
        else:
            print(f"   {reachable_icon} {r['server']:30s}  UNREACHABLE ({r.get('error', 'unknown')})")
            print(f"      └─ {desc}")
    print()
    if summary["overall_status"] == "ALERT":
        print("❌  CERT-In Alert: Clock drift exceeded threshold or all NTP servers unreachable.")
        print("    Action required: Verify chrony/systemd-timesyncd is configured for NPL/NIC servers.")
        print("    See: docs/ntp_compliance.md\n")
    else:
        print("✅  Clock is synchronized with Indian government NTP sources.\n")


def main():
    parser = argparse.ArgumentParser(
        description="CERT-In / DPDP NTP compliance check — NPL and NIC server drift verification."
    )
    parser.add_argument(
        "--all", dest="query_all", action="store_true",
        help="Query ALL servers (don't stop at first reachable). Useful for full audit reports."
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Output machine-readable JSON (suitable for log aggregators like CloudWatch/Stackdriver)."
    )
    parser.add_argument(
        "--threshold", type=float, default=2.0,
        help="Maximum acceptable drift in seconds (default: 2.0). Exit code 1 if exceeded."
    )
    parser.add_argument(
        "--timeout", type=float, default=3.0,
        help="Socket timeout per server in seconds (default: 3.0)."
    )
    parser.add_argument(
        "--servers", type=str, default=None,
        help="Comma-separated list of NTP server hostnames to query (overrides default NPL/NIC list)."
    )
    args = parser.parse_args()

    if args.servers:
        servers = [(s.strip(), "Custom") for s in args.servers.split(",") if s.strip()]
    else:
        servers = _DEFAULT_SERVERS

    exit_code = run_check(
        servers=servers,
        timeout=args.timeout,
        threshold=args.threshold,
        query_all=args.query_all,
        json_output=args.json_output,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
