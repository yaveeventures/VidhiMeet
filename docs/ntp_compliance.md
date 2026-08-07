# NTP Time Synchronization — Compliance Runbook

**Regulation**: CERT-In Directions 2022 (Clause 2(vi)) · DPDP Act 2023 (§8 — Accuracy)  
**Scope**: All servers hosting the API backend, PostgreSQL database, Redis cache, and payment gateway integrations.

---

## Why This Matters

Under CERT-In's mandatory cybersecurity directions, **all ICT infrastructure must synchronize system clocks with National Physical Laboratory (NPL) or National Informatics Centre (NIC) NTP servers**. This ensures that timestamps across:

- Application audit logs (`audit_logs` table)
- Payment gateway transaction records (PhonePe / Stripe)
- Video consultation session logs (Daily.co)
- PostgreSQL transaction logs and WAL records
- Redis command logs and expiry records

…all agree precisely, enabling coherent **forensic reconstruction** if a cyber incident occurs and needs to be reported to CERT-In within 6 hours.

---

## Indian Government NTP Servers

| Priority | Hostname            | Organization                            |
|----------|---------------------|-----------------------------------------|
| 1 (Primary)  | `time.nplindia.org` | National Physical Laboratory (CSIR-NPL) |
| 2 (Secondary) | `time.nplindia.in`  | National Physical Laboratory (alternate) |
| 3 (Tertiary)  | `time.nic.in`       | National Informatics Centre (NIC)        |
| 4 (Fallback)  | `pool.ntp.org`      | International NTP Pool (last resort)    |

> [!IMPORTANT]
> Production servers **must** use NPL or NIC as the primary NTP source. The `pool.ntp.org` fallback is only for development environments.

---

## Application-Level Implementation

The application queries these servers directly at the code level in two ways:

1. **Startup drift check** — On every `uvicorn` start, `check_clock_drift()` is called and the result is logged. A `CRITICAL` log entry is emitted if drift exceeds ±2 seconds.

2. **Audit log timestamps** — Every call to `audit()` in `backend/services.py` stamps the `AuditLog.created_at` with `ntp_now()` — a timestamp sourced directly from NPL/NIC via UDP NTP query.

3. **Admin health endpoint** — `GET /api/v1/admin/ntp-status` (admin-only) returns real-time drift data.

4. **Cron-based drift check** — `scripts/ntp_sync_check.py` runs on each server every 15 minutes.

---

## Host OS Configuration (Linux Servers)

The OS-level clock must also be synchronized. Choose one:

### Option A: chrony (Recommended for production)

```bash
sudo apt install chrony          # Ubuntu/Debian
# or
sudo yum install chrony          # RHEL/Amazon Linux
```

Edit `/etc/chrony.conf` and replace the default pool lines with:

```conf
# Indian Government NTP Servers (CERT-In compliant)
server time.nplindia.org iburst prefer
server time.nplindia.in  iburst
server time.nic.in       iburst

# International fallback (development/non-production only)
# server pool.ntp.org iburst

# Allow only localhost to query this machine as a time source
allow 127.0.0.1
```

```bash
sudo systemctl enable --now chronyd
sudo chronyc tracking      # verify synchronization
sudo chronyc sources -v    # confirm NPL/NIC sources are selected
```

### Option B: systemd-timesyncd (Simpler, minimal installations)

Edit `/etc/systemd/timesyncd.conf`:

```ini
[Time]
NTP=time.nplindia.org time.nplindia.in time.nic.in
FallbackNTP=pool.ntp.org
```

```bash
sudo systemctl enable --now systemd-timesyncd
timedatectl show-timesync --all   # verify
timedatectl status                # confirm synchronized=yes
```

---

## Docker / Container Configuration

Containers **inherit the host system clock** via the kernel. No separate NTP client is needed inside containers.

**Critical requirement**: The Docker host OS must be NTP-synchronized with NPL/NIC (see above). Verify:

```bash
# On the Docker host
chronyc tracking
# Expected: "System time" drift should be < 1ms to reference server
```

The `docker-compose.yml` uses `restart: unless-stopped` — ensure the host clock is correct before any container restart following a system maintenance window.

---

## PostgreSQL Configuration

PostgreSQL uses the system clock. Once the host OS is configured with chrony/systemd-timesyncd, PostgreSQL timestamps will be aligned automatically.

Verify timestamp alignment after configuration:

```sql
-- Run this query and compare with: date -u (on host)
SELECT NOW() AT TIME ZONE 'UTC';

-- Check WAL/transaction log timestamps match NTP time
SELECT pg_postmaster_start_time() AT TIME ZONE 'UTC';
```

For production, enable PostgreSQL logging of connection timestamps:

```conf
# postgresql.conf
log_timezone = 'Asia/Kolkata'   # IST for human-readable log review
```

---

## Redis Configuration

Redis uses the system clock for key expiry and RDB/AOF snapshot timestamps. Once the host is NTP-synchronized:

```bash
# Verify Redis server time matches NTP
redis-cli TIME
# Returns: [Unix timestamp seconds, microseconds]
# Compare with: date +%s
```

---

## Cron Job Setup (All Servers)

Run `scripts/ntp_sync_check.py` every 15 minutes on **all servers** (API, DB, Redis):

```bash
# Add to crontab (crontab -e)
*/15 * * * * cd /opt/lawyergrid && python3 -m scripts.ntp_sync_check --json 2>&1 | logger -t ntp_compliance
```

For CloudWatch / Stackdriver log-based alerting, parse for:
- `"overall_status": "ALERT"` — trigger an ops incident
- `NTP_STARTUP_DRIFT_ALERT` — in application logs

Manual one-off check (human-readable):
```bash
python -m scripts.ntp_sync_check --all
```

Manual one-off check (all servers, JSON for log ingestion):
```bash
python -m scripts.ntp_sync_check --all --json
```

---

## Environment Variables

Override default NTP settings in `.env` or via the container environment:

| Variable               | Default                                          | Description                                  |
|------------------------|--------------------------------------------------|----------------------------------------------|
| `NTP_SERVERS`          | `time.nplindia.org,time.nplindia.in,time.nic.in,pool.ntp.org` | Comma-separated ordered server list |
| `NTP_TIMEOUT_SECONDS`  | `3.0`                                            | Socket timeout per server (seconds)          |
| `NTP_MAX_DRIFT_SECONDS`| `2.0`                                            | CERT-In alert threshold (seconds)            |
| `NTP_SYNC_ON_STARTUP`  | `true`                                           | Run drift check on app startup               |

---

## Incident Response

If `within_tolerance: false` is returned by the admin endpoint or cron script:

1. **Check host sync status**: `chronyc tracking` or `timedatectl status`
2. **Verify NPL/NIC reachability**: `ntpdate -q time.nplindia.org`
3. **Force re-sync**: `sudo chronyc makestep` (forces immediate clock correction)
4. **Check firewall rules**: Ensure UDP port 123 is open outbound to `time.nplindia.org`, `time.nplindia.in`, `time.nic.in`
5. **Review audit logs**: All `AuditLog.created_at` timestamps during the drift window should be flagged in any forensic report submitted to CERT-In.

---

## References

- [CERT-In Directions 2022 (MeitY)](https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf) — Clause 2(vi): NTP synchronization mandate
- [CSIR-NPL Time Services](https://www.nplindia.org/time-services/) — NPL official NTP documentation
- [NIC Time Server](https://www.nic.in/) — NIC infrastructure services
- [RFC 5905 — NTPv4 Specification](https://www.rfc-editor.org/rfc/rfc5905)
- [chrony documentation](https://chrony-project.org/documentation.html)
