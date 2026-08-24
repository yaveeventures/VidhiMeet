# ==============================================================================
# VidhiMeet — Cloudflare Edge Security Infrastructure (Terraform)
# Zone: vidhimeet.in
# Provider: cloudflare/cloudflare >= 4.0
# ==============================================================================

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.20"
    }
  }
}

variable "cloudflare_zone_id" {
  type        = string
  description = "The Cloudflare Zone ID for vidhimeet.in"
}

variable "cloudflare_account_id" {
  type        = string
  description = "The Cloudflare Account ID"
}

# ------------------------------------------------------------------------------
# LAYER 1: Edge-Level Rate Limiting Ruleset (http_ratelimit phase)
# Protects authentication endpoints from credential stuffing & brute-force bots
# ------------------------------------------------------------------------------
resource "cloudflare_ruleset" "edge_rate_limiting" {
  zone_id     = var.cloudflare_zone_id
  name        = "VidhiMeet Auth Edge Rate Limiting"
  description = "Edge rate limiting rules protecting login, registration, and password reset routes."
  kind        = "zone"
  phase       = "http_ratelimit"

  rules {
    action      = "block"
    description = "Credential Stuffing & Auth Brute Force Protection (10 req/min limit)"
    expression  = "(http.request.uri.path in {\"/api/v1/auth/login\" \"/api/v1/auth/register\" \"/api/v1/auth/forgot-password\" \"/api/v1/auth/reset-password\" \"/api/v1/auth/google\" \"/admin-login.html\"})"
    enabled     = true

    ratelimit {
      characteristics        = ["ip.src"]
      period                 = 60
      requests_per_period    = 10
      mitigation_timeout     = 600
      counting_expression    = "http.request.response.status in {200 401 403 409 422}"
    }
  }

  rules {
    action      = "managed_challenge"
    description = "Tier 2 Burst Rate Limiting on Refresh & Auth Operations (30 req/min)"
    expression  = "(http.request.uri.path starts_with \"/api/v1/auth/\")"
    enabled     = true

    ratelimit {
      characteristics        = ["ip.src"]
      period                 = 60
      requests_per_period    = 30
      mitigation_timeout     = 300
    }
  }
}

# ------------------------------------------------------------------------------
# LAYER 2: Advanced Bot Management Ruleset (http_request_firewall_custom phase)
# Challenges scraping & automated reconnaissance on high-value/public pages
# ------------------------------------------------------------------------------
resource "cloudflare_ruleset" "bot_management" {
  zone_id     = var.cloudflare_zone_id
  name        = "VidhiMeet Bot Management & Scraping Shield"
  description = "Automated bot challenge rules for pricing, lawyers directory, checkout, and API docs."
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  # Rule 2.1: Block Verified Bad Bots & Scanners globally
  rules {
    action      = "block"
    description = "Block Known Malicious Scanners & Automated Reconnaissance Bots"
    expression  = "(cf.client.bot or http.user_agent matches \"(?i)(nikto|sqlmap|nmap|dirbuster|gobuster|wpscan|masscan|zgrab|acunetix|nessus|python-requests|aiohttp|httpx|curl|wget)\") and not cf.bot_management.verified_bot"
    enabled     = true
  }

  # Rule 2.2: Challenge Low Bot Score traffic on High-Value / Pricing & Directory Pages
  rules {
    action      = "managed_challenge"
    description = "Challenge Automated Scraping on Lawyer Directory & Pricing Pages"
    expression  = "(http.request.uri.path in {\"/\" \"/index.html\" \"/lawyer.html\" \"/api/v1/lawyers\" \"/api/v1/public/stats\"}) and (cf.bot_management.score < 30 and not cf.bot_management.verified_bot)"
    enabled     = true
  }

  # Rule 2.3: Strict Challenge for API Documentation & Reconnaissance Endpoints
  rules {
    action      = "managed_challenge"
    description = "Protect API Docs (/docs, /openapi.json, /redoc) from Reconnaissance Scanners"
    expression  = "(http.request.uri.path in {\"/docs\" \"/openapi.json\" \"/redoc\"}) and (cf.bot_management.score < 40 and not cf.bot_management.verified_bot)"
    enabled     = true
  }

  # Rule 2.4: Managed Challenge for Checkout & Drafting Intakes
  rules {
    action      = "managed_challenge"
    description = "Bot Verification on Checkout & Drafting Requests"
    expression  = "(http.request.uri.path starts_with \"/api/v1/bookings\" or http.request.uri.path starts_with \"/api/v1/drafting\") and (http.request.method eq \"POST\") and (cf.bot_management.score < 25 and not cf.bot_management.verified_bot)"
    enabled     = true
  }
}

# ------------------------------------------------------------------------------
# LAYER 3: Custom WAF Ruleset (http_request_firewall_custom phase)
# Immediate edge blocking for SQLi, XSS, Path Traversal, and Enumeration payloads
# ------------------------------------------------------------------------------
resource "cloudflare_ruleset" "custom_waf" {
  zone_id     = var.cloudflare_zone_id
  name        = "VidhiMeet Custom Edge WAF Payload Shield"
  description = "Custom WAF expressions catching SQLi, XSS, Path Traversal, and Enumeration at the edge."
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  # Rule 3.1: SQL Injection (SQLi) Inspection
  rules {
    action      = "block"
    description = "WAF Edge Shield: SQL Injection Payload Defense"
    expression  = "(http.request.uri.query matches \"(?i)(union\\s+select|select\\s+.*\\s+from|insert\\s+into|delete\\s+from|drop\\s+table|update\\s+.*\\s+set|exec\\(|waitfor\\s+delay|information_schema|pg_sleep)\" or http.request.full_uri matches \"(?i)(%27|%22).*--|(\\+|%20)or(\\+|%20)1=1\")"
    enabled     = true
  }

  # Rule 3.2: Cross-Site Scripting (XSS) Inspection
  rules {
    action      = "block"
    description = "WAF Edge Shield: Cross-Site Scripting (XSS) Payload Defense"
    expression  = "(http.request.uri.query matches \"(?i)(<script|javascript:|onerror\\s*=|onload\\s*=|eval\\(|document\\.cookie|window\\.location|<iframe|<img\\s+src=)\" or http.request.full_uri matches \"(?i)(%3Cscript|javascript%3A|onerror%3D|onload%3D)\")"
    enabled     = true
  }

  # Rule 3.3: Path & Directory Traversal Inspection
  rules {
    action      = "block"
    description = "WAF Edge Shield: Path Traversal & LFI Payload Defense"
    expression  = "(http.request.uri.path matches \"(?i)(\\.\\./|\\.\\.\\\\|/etc/passwd|/win\\.ini|/proc/self|cmd\\.exe|/bin/sh|\\.env|\\.git|wp-config\\.php|phpinfo)\")"
    enabled     = true
  }

  # Rule 3.4: Account & Data Enumeration Payloads
  rules {
    action      = "block"
    description = "WAF Edge Shield: Account & IDOR Enumeration Attack Defense"
    expression  = "(http.request.uri.query matches \"(?i)(user_id\\[\\]|id\\[\\]|admin=true|role=admin|uid=0)\" or http.request.headers[\"user-agent\"][0] eq \"\")"
    enabled     = true
  }
}
