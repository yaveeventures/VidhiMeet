# 🌐 Domain DNS & SSL/TLS 1.3 — Production Configuration Runbook

**Standard**: RFC 8446 (TLS 1.3) · CERT-In Directions 2022 · DPDP Act 2023 (§8 — Confidentiality)  
**Scope**: Cloudflare DNS records, Cloudflare Edge WAF, Nginx reverse proxy, and Let's Encrypt TLS 1.3 multi-SAN certificates for `vidhimeet.in` and subdomains (`www`, `lawyer`, `admin`).

---

## 1. End-to-End Encryption Architecture

VidhiMeet enforces a **Strict Zero-Unencrypted-Transit** model where every hop across the public internet is encrypted using TLS 1.3:

```
┌─────────────────────────────────┐
│     Client / Browser / App      │
└────────────────┬────────────────┘
                 │
                 │ HTTPS (TLS 1.3 / HTTP/3 QUIC)
                 │ Strict Transport Security (HSTS 2-Year Preload)
                 ▼
┌─────────────────────────────────┐
│     Cloudflare Edge Network     │
│   (WAF Shield, Bot Challenge,   │
│    Edge Rate Limiting, DNS)     │
└────────────────┬────────────────┘
                 │
                 │ HTTPS (TLS 1.3 / Port 443)
                 │ Mode: Full (Strict) SSL
                 │ Authenticated Origin / Let's Encrypt SAN Cert
                 ▼
┌─────────────────────────────────┐
│       Nginx Reverse Proxy       │
│   • Restores CF-Connecting-IP   │
│   • OCSP Stapling & Session TTL │
│   • HTTP/2, WebSockets, & SSE   │
└────────────────┬────────────────┘
                 │
                 │ Reverse Proxy (127.0.0.1:8000 / Internal Network)
                 ▼
┌─────────────────────────────────┐
│    FastAPI Application Cluster  │
└─────────────────────────────────┘
```

---

## 2. Cloudflare DNS Infrastructure

Defined in [`cloudflare/main.tf`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/cloudflare/main.tf):

### 2.1 Zone DNS Records

| Record Type | Host / Name | Target / Value | Proxy Status | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **A** | `vidhimeet.in` | `${var.origin_server_ip}` | **Proxied (Orange Cloud)** | Apex domain routing to origin server via Cloudflare Edge |
| **CNAME** | `www` | `vidhimeet.in` | **Proxied (Orange Cloud)** | Canonical www subdomain |
| **CNAME** | `lawyer` | `vidhimeet.in` | **Proxied (Orange Cloud)** | Advocate Portal & Practice Management UI (`lawyer.html`) |
| **CNAME** | `admin` | `vidhimeet.in` | **Proxied (Orange Cloud)** | Admin Security Console (`admin.html`) |

### 2.2 Global Cloudflare Edge SSL/TLS Settings

Applied via `cloudflare_zone_settings_override`:
- **SSL Mode**: `strict` (Full Strict — origin certificate must be valid and signed by a trusted CA or Cloudflare Origin CA).
- **Minimum TLS Version**: `1.2` (Restricts insecure TLS 1.0/1.1 protocols).
- **TLS 1.3**: `on` (Enables 0-RTT handshakes and modern AEAD ciphers).
- **Always Use HTTPS**: `on` (Edge 301 redirection for all incoming port 80 traffic).
- **Automatic HTTPS Rewrites**: `on` (Prevents mixed content warnings on legacy assets).
- **HTTP/3 (with QUIC)**: `on` (High-performance UDP transport for mobile video consultations).
- **HSTS Preload**: `max-age=63072000; includeSubDomains; preload; nosniff` (Mandatory 2-year browser enforcement).

---

## 3. Nginx Reverse Proxy Hardening (`nginx/vidhimeet.conf`)

Located at [`nginx/vidhimeet.conf`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/nginx/vidhimeet.conf):

### 3.1 Cloudflare Real-IP Restoration
Because Cloudflare acts as a reverse proxy, the TCP connection to Nginx originates from Cloudflare's IP ranges. To ensure:
1. Accurate IP-based rate limiting in `backend/rate_limiter.py`
2. Forensic CERT-In audit logging in `audit_logs` table
3. Geo-blocking & abuse containment

Nginx configures `set_real_ip_from` across all official Cloudflare IPv4 and IPv6 CIDRs, restoring the real client IP via `real_ip_header CF-Connecting-IP`.

### 3.2 Canonical Domain Redirection
1. **HTTP -> HTTPS**: Port 80 requests for `vidhimeet.in`, `www.vidhimeet.in`, `lawyer.vidhimeet.in`, and `admin.vidhimeet.in` are permanently redirected (301) to `https://$host$request_uri`.
2. **WWW -> Non-WWW**: All `https://www.vidhimeet.in` traffic is canonically redirected (301) to `https://vidhimeet.in`.

### 3.3 TLS 1.3 Protocols & Cipher Suite
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
```

### 3.4 Real-time Protocol Handlers
- **WebSockets** (`/api/v1/ws/`): Configured with `Upgrade $http_upgrade`, `Connection "Upgrade"`, and `proxy_read_timeout 86400s` for uninterrupted video consultation chat.
- **Server-Sent Events** (`/api/v1/events/`): Configured with `proxy_buffering off; chunked_transfer_encoding off;` for instant client notifications.

---

## 4. Let's Encrypt SSL Provisioning (`scripts/setup_domain_ssl.sh`)

Automated installation and provisioning script: [`scripts/setup_domain_ssl.sh`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/scripts/setup_domain_ssl.sh).

### 4.1 Running the Provisioning Script on Ubuntu/Debian

```bash
# Execute with your domain and notification admin email:
sudo bash scripts/setup_domain_ssl.sh vidhimeet.in admin@vidhimeet.in
```

### 4.2 Multi-SAN Certificate Coverage
Certbot requests a single certificate covering all platform entry points:
```bash
certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email admin@vidhimeet.in \
    -d vidhimeet.in \
    -d www.vidhimeet.in \
    -d lawyer.vidhimeet.in \
    -d admin.vidhimeet.in \
    --redirect
```

### 4.3 Automated Certificate Renewal
Certbot installs a systemd timer that triggers renewals twice daily:
```bash
# Verify renewal timer status
systemctl status certbot.timer

# Run a dry-run test
sudo certbot renew --dry-run
```

---

## 5. Automated Diagnostic & Health Verification

VidhiMeet includes an automated DNS & SSL diagnostic tool: [`scripts/check_domain_ssl.py`](file:///d:/Yavee%20Ventures/Projects/VidhiMeet/scripts/check_domain_ssl.py).

### 5.1 Running the Audit Tool

```powershell
# Audit all VidhiMeet domains (apex, www, lawyer, admin):
python scripts/check_domain_ssl.py

# Audit specific domain:
python scripts/check_domain_ssl.py --domains vidhimeet.in

# Machine-readable JSON output for CI/CD:
python scripts/check_domain_ssl.py --json
```

### 5.2 Diagnostic Verification Output Example

```
================================================================================
 [*] VidhiMeet Domain DNS & SSL/TLS 1.3 Infrastructure Audit Report
================================================================================

[Domain] vidhimeet.in
  [+] DNS Resolution: OK -> 104.21.35.110
  [+] SSL Protocol:   [TLS 1.3] via TLS_AES_256_GCM_SHA384
  [+] Certificate:    Issued by Google Trust Services (Expires in 84 days)
  [+] Covered SANs:   vidhimeet.in
  [+] HSTS Status:    ENABLED (max-age=63072000; includeSubDomains; preload)

================================================================================
[SUCCESS] All VidhiMeet domains resolved with valid SSL/TLS certificates.
================================================================================
```

---

## 6. Troubleshooting & Common Scenarios

### Error 526: Invalid SSL Certificate (Cloudflare)
* **Cause**: Cloudflare is set to `Full (strict)` mode, but the origin server has an expired, self-signed, or hostname-mismatched certificate.
* **Fix**: Run `sudo certbot certonly --nginx -d vidhimeet.in -d www.vidhimeet.in -d lawyer.vidhimeet.in -d admin.vidhimeet.in` to ensure Let's Encrypt covers all subdomains, or generate a 15-year Cloudflare Origin Certificate from the Cloudflare Dashboard (`SSL/TLS -> Origin Server`).

### Too Many Redirects (ERR_TOO_MANY_REDIRECTS)
* **Cause**: Cloudflare is set to `Flexible` mode while Nginx forces port 80 -> 443 redirects.
* **Fix**: In the Cloudflare Dashboard, navigate to **SSL/TLS** and change the encryption mode from **Flexible** to **Full (strict)**.
