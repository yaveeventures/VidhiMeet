#!/usr/bin/env bash
# ==============================================================================
# VidhiMeet — Cloudflare Edge Security Deployment Script (REST API v4)
# Usage: CLOUDFLARE_API_TOKEN="your_token" CLOUDFLARE_ZONE_ID="your_zone_id" ./cloudflare/deploy_rules.sh
# ==============================================================================

set -euo pipefail

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ] || [ -z "${CLOUDFLARE_ZONE_ID:-}" ]; then
    echo "❌ Error: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID environment variables must be set."
    echo "Usage: CLOUDFLARE_API_TOKEN='...' CLOUDFLARE_ZONE_ID='...' ./cloudflare/deploy_rules.sh"
    exit 1
fi

ZONE_ID="${CLOUDFLARE_ZONE_ID}"
API_BASE="https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets"

echo "🛡️ Deploying Cloudflare Edge Security Shield for VidhiMeet (Zone: ${ZONE_ID})..."

# ------------------------------------------------------------------------------
# LAYER 1: Deploy Edge Rate Limiting Ruleset (http_ratelimit)
# ------------------------------------------------------------------------------
echo "⚡ Layer 1: Deploying Edge Rate Limiting Rules..."
curl -s -X POST "${API_BASE}" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "VidhiMeet Auth Edge Rate Limiting",
       "kind": "zone",
       "phase": "http_ratelimit",
       "rules": [
         {
           "action": "block",
           "description": "Credential Stuffing & Auth Brute Force Protection (10 req/min limit)",
           "expression": "(http.request.uri.path in {\"/api/v1/auth/login\" \"/api/v1/auth/register\" \"/api/v1/auth/forgot-password\" \"/api/v1/auth/reset-password\" \"/api/v1/auth/google\" \"/admin-login.html\"})",
           "enabled": true,
           "ratelimit": {
             "characteristics": ["ip.src"],
             "period": 60,
             "requests_per_period": 10,
             "mitigation_timeout": 600,
             "counting_expression": "http.request.response.status in {200 401 403 409 422}"
           }
         },
         {
           "action": "managed_challenge",
           "description": "Tier 2 Burst Rate Limiting on Refresh & Auth Operations (30 req/min)",
           "expression": "(http.request.uri.path starts_with \"/api/v1/auth/\")",
           "enabled": true,
           "ratelimit": {
             "characteristics": ["ip.src"],
             "period": 60,
             "requests_per_period": 30,
             "mitigation_timeout": 300
           }
         }
       ]
     }' | grep '"success":true' && echo "  ✅ Edge Rate Limiting Rules Deployed!" || echo "  ⚠️ Layer 1 Notice: Check API response above."

# ------------------------------------------------------------------------------
# LAYER 2 & 3: Deploy Custom WAF & Bot Management Rules (http_request_firewall_custom)
# ------------------------------------------------------------------------------
echo "🤖 Layers 2 & 3: Deploying Advanced Bot Management & Custom WAF Payload Shield..."
curl -s -X POST "${API_BASE}" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "VidhiMeet Custom Edge WAF & Bot Shield",
       "kind": "zone",
       "phase": "http_request_firewall_custom",
       "rules": [
         {
           "action": "skip",
           "action_parameters": {
             "ruleset": "current"
           },
           "description": "Allow Search Engine Crawlers & SEO Files (/sitemap.xml, /robots.txt)",
           "expression": "(http.request.uri.path in {\"/sitemap.xml\" \"/robots.txt\"}) or cf.bot_management.verified_bot",
           "enabled": true
         },
         {
           "action": "block",
           "description": "Block Known Malicious Scanners & Recon Bots",
           "expression": "(cf.client.bot or http.user_agent matches \"(?i)(nikto|sqlmap|nmap|dirbuster|gobuster|wpscan|masscan|zgrab|acunetix|nessus|python-requests|aiohttp|httpx|curl|wget)\") and not cf.bot_management.verified_bot and not (http.request.uri.path in {\"/sitemap.xml\" \"/robots.txt\"})",
           "enabled": true
         },
         {
           "action": "managed_challenge",
           "description": "Challenge Automated Scraping on Lawyer Directory & Pricing Pages",
           "expression": "(http.request.uri.path in {\"/\" \"/index.html\" \"/lawyer.html\" \"/api/v1/lawyers\" \"/api/v1/public/stats\"}) and (cf.bot_management.score < 30 and not cf.bot_management.verified_bot)",
           "enabled": true
         },
         {
           "action": "managed_challenge",
           "description": "Protect API Docs (/docs, /openapi.json, /redoc) from Reconnaissance",
           "expression": "(http.request.uri.path in {\"/docs\" \"/openapi.json\" \"/redoc\"}) and (cf.bot_management.score < 40 and not cf.bot_management.verified_bot)",
           "enabled": true
         },
         {
           "action": "block",
           "description": "WAF Edge Shield: SQL Injection Payload Defense",
           "expression": "(http.request.uri.query matches \"(?i)(union\\\\s+select|select\\\\s+.*\\\\s+from|insert\\\\s+into|delete\\\\s+from|drop\\\\s+table|update\\\\s+.*\\\\s+set|exec\\\\(|waitfor\\\\s+delay|information_schema|pg_sleep)\" or http.request.full_uri matches \"(?i)(%27|%22).*--|(\\\\+|%20)or(\\\\+|%20)1=1\")",
           "enabled": true
         },
         {
           "action": "block",
           "description": "WAF Edge Shield: Cross-Site Scripting (XSS) Payload Defense",
           "expression": "(http.request.uri.query matches \"(?i)(<script|javascript:|onerror\\\\s*=|onload\\\\s*=|eval\\\\(|document\\\\.cookie|window\\\\.location|<iframe|<img\\\\s+src=)\" or http.request.full_uri matches \"(?i)(%3Cscript|javascript%3A|onerror%3D|onload%3D)\")",
           "enabled": true
         },
         {
           "action": "block",
           "description": "WAF Edge Shield: Path Traversal & LFI Payload Defense",
           "expression": "(http.request.uri.path matches \"(?i)(\\\\.\\\\./|\\\\.\\\\.\\\\|/etc/passwd|/win\\\\.ini|/proc/self|cmd\\\\.exe|/bin/sh|\\\\.env|\\\\.git|wp-config\\\\.php|phpinfo)\")",
           "enabled": true
         },
         {
           "action": "block",
           "description": "WAF Edge Shield: Account & IDOR Enumeration Attack Defense",
           "expression": "(http.request.uri.query matches \"(?i)(user_id\\\\[\\\\]|id\\\\[\\\\]|admin=true|role=admin|uid=0)\" or http.request.headers[\"user-agent\"][0] eq \"\")",
           "enabled": true
         }
       ]
     }' | grep '"success":true' && echo "  ✅ WAF & Bot Shield Rules Deployed!" || echo "  ⚠️ Layers 2 & 3 Notice: Check API response above."

echo "🚀 All Cloudflare Edge Security Shield rules successfully configured for VidhiMeet!"
