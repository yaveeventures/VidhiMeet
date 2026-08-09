"""
ntp_time.py
-----------
NTP time synchronization for CERT-In and DPDP forensic timestamp compliance.

Queries government NTP servers in priority order:
  1. time.nplindia.org  — National Physical Laboratory (NPL), India (primary)
  2. time.nplindia.in   — NPL alternate hostname (secondary)
  3. time.nic.in        — National Informatics Centre (NIC), India (tertiary)
  4. pool.ntp.org       — International pool (last-resort fallback)

Uses raw UDP sockets + NTP v3 packet structure (RFC 5905) — no third-party
ntplib dependency required.

All application timestamps intended for audit logs, payment records, and
forensic evidence should use ntp_now() from this module.
"""

import structlog
import socket
import struct
from datetime import datetime, timedelta, timezone
from typing import TypedDict

from .config import get_settings

log = structlog.get_logger("ntp_time")

# ── NTP Protocol Constants (RFC 5905) ─────────────────────────────────────────
_NTP_PORT = 123
_NTP_PACKET_FORMAT = "!B B b b 11I"
_NTP_DELTA = 2208988800  # Seconds between 1900-01-01 and 1970-01-01 (Unix epoch)
_NTP_PACKET = b"\x1b" + 47 * b"\0"  # LI=0, Version=3, Mode=3 (client)

# IST offset: UTC+05:30
_IST = timezone(timedelta(hours=5, minutes=30))


class NtpStatus(TypedDict):
    ntp_server: str
    synced_at: str          # ISO-8601 UTC string
    system_time: str        # ISO-8601 UTC string
    drift_seconds: float    # Positive = system ahead of NTP; negative = behind
    within_tolerance: bool


def _query_ntp_server(host: str, timeout: float) -> datetime | None:
    """
    Send a single NTP client request to *host* and return the transmit
    timestamp as a UTC-aware datetime, or None on any error.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(_NTP_PACKET, (host, _NTP_PORT))
            data, _ = sock.recvfrom(48)
        if len(data) < 48:
            return None
        # Transmit timestamp is at bytes 40-47 (two 32-bit words: seconds + fraction)
        unpacked = struct.unpack(_NTP_PACKET_FORMAT, data)
        ntp_sec = unpacked[10]
        if ntp_sec < _NTP_DELTA:
            return None
        tx_seconds = ntp_sec - _NTP_DELTA  # Convert NTP epoch → Unix epoch
        tx_fraction = unpacked[11]
        tx_microseconds = tx_fraction * 1_000_000 / (2 ** 32)
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
            seconds=tx_seconds, microseconds=tx_microseconds
        )
    except (OSError, struct.error) as exc:
        log.debug("NTP query failed", host=host, error=str(exc))
        return None


def _get_servers() -> list[str]:
    """Return the ordered list of NTP servers from settings."""
    settings = get_settings()
    return [s.strip() for s in settings.ntp_servers.split(",") if s.strip()]


def ntp_now() -> datetime:
    """
    Return the current time as a UTC-aware datetime sourced from the first
    reachable NPL/NIC NTP server.

    Falls back to datetime.now(UTC) if ALL servers are unreachable, logging
    a CRITICAL warning so ops teams are alerted.
    """
    settings = get_settings()
    timeout = settings.ntp_timeout_seconds

    for server in _get_servers():
        result = _query_ntp_server(server, timeout)
        if result is not None:
            log.debug("NTP time from %s: %s", server, result.isoformat())
            return result

    log.critical(
        "NTP_SYNC_FAILED: All NTP servers unreachable (%s). "
        "Falling back to system clock — timestamps may not be forensically authoritative.",
        ", ".join(_get_servers()),
    )
    return datetime.now(timezone.utc)


def ntp_now_ist() -> datetime:
    """
    Return the current NPL/NIC-sourced time in Indian Standard Time (UTC+5:30).
    Useful for display, logging, and audit records that require IST context.
    """
    return ntp_now().astimezone(_IST)


def check_clock_drift() -> NtpStatus:
    """
    Compare the system clock against the first reachable NTP server.

    Returns a structured dict with drift details and a within_tolerance flag.
    Logs a WARNING if drift exceeds the configured threshold.
    """
    settings = get_settings()
    timeout = settings.ntp_timeout_seconds
    max_drift = settings.ntp_max_drift_seconds

    system_time = datetime.now(timezone.utc)
    server_used = "none"
    ntp_time_val: datetime | None = None

    for server in _get_servers():
        result = _query_ntp_server(server, timeout)
        if result is not None:
            ntp_time_val = result
            server_used = server
            break

    if ntp_time_val is None:
        log.critical(
            "NTP_DRIFT_CHECK_FAILED: All NTP servers unreachable. "
            "Cannot verify clock accuracy for forensic timestamp compliance."
        )
        return NtpStatus(
            ntp_server="unavailable",
            synced_at=system_time.isoformat(),
            system_time=system_time.isoformat(),
            drift_seconds=0.0,
            within_tolerance=False,
        )

    drift = (system_time - ntp_time_val).total_seconds()
    within_tolerance = abs(drift) <= max_drift

    if not within_tolerance:
        log.warning(
            "NTP_CLOCK_DRIFT_ALERT: System clock is %.3fs %s NTP time (server: %s). "
            "Threshold is ±%.1fs. Timestamps may be unreliable for legal forensics.",
            abs(drift),
            "ahead of" if drift > 0 else "behind",
            server_used,
            max_drift,
        )
    else:
        log.info(
            "NTP_SYNC_OK: drift=%.3fs server=%s synced_at=%s",
            drift,
            server_used,
            ntp_time_val.isoformat(),
        )

    return NtpStatus(
        ntp_server=server_used,
        synced_at=ntp_time_val.isoformat(),
        system_time=system_time.isoformat(),
        drift_seconds=round(drift, 6),
        within_tolerance=within_tolerance,
    )
