import logging
from ..ntp_time import check_clock_drift, ntp_now, ntp_now_ist

log = logging.getLogger("fastapi")

def verify_ntp_compliance() -> dict:
    """Run CERT-In / DPDP compliant NTP clock drift check."""
    status = check_clock_drift()
    if not status["within_tolerance"]:
        log.warning(
            "NTP drift alert: server=%s drift=%.3fs",
            status.get("ntp_server"),
            status.get("drift_seconds", 0.0)
        )
    return status
