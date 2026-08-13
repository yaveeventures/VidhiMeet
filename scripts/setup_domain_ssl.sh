#!/usr/bin/env bash
# ==============================================================================
# VidhiMeet — Domain & Let's Encrypt SSL Provisioning Script
# Usage: sudo bash scripts/setup_domain_ssl.sh yourdomain.com admin@yourdomain.com
# ==============================================================================

set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ Usage: sudo bash scripts/setup_domain_ssl.sh <DOMAIN_NAME> <ADMIN_EMAIL>"
    echo "   Example: sudo bash scripts/setup_domain_ssl.sh vidhimeet.com admin@vidhimeet.com"
    exit 1
fi

echo "🚀 Provisioning Domain & SSL for: ${DOMAIN} (Admin: ${EMAIL})"

# 1. Install Nginx & Certbot dependencies
echo "📦 Installing Nginx, Certbot, and Python Certbot Nginx plugin..."
apt-get update -q
apt-get install -y -q nginx certbot python3-certbot-nginx curl ufw

# 2. Configure Firewall rules for Nginx
echo "🛡️ Enabling HTTP & HTTPS ports in Firewall (UFW)..."
ufw allow 'Nginx Full' || true

# 3. Create Nginx Site Configuration
NGINX_CONF="/etc/nginx/sites-available/vidhimeet.conf"
echo "📝 Generating Nginx configuration at ${NGINX_CONF}..."

cat <<EOF > "$NGINX_CONF"
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN} lawyer.${DOMAIN} admin.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN} lawyer.${DOMAIN} admin.${DOMAIN};

    # Temporary self-signed or Certbot managed paths
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 15M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400s;
    }

    location /api/v1/events/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_cache off;
    }
}
EOF

# 4. Enable Nginx site
echo "🔗 Enabling Nginx site configuration..."
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/vidhimeet.conf
rm -f /etc/nginx/sites-enabled/default || true

# Test Nginx syntax
nginx -t

# Reload Nginx
systemctl reload nginx

# 5. Obtain Let's Encrypt SSL Certificate
echo "🔒 Requesting Let's Encrypt SSL Certificates via Certbot..."
certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.${DOMAIN}" \
    -d "lawyer.${DOMAIN}" \
    -d "admin.${DOMAIN}" \
    --redirect

# 6. Test Automatic Certbot Renewal
echo "🔄 Verifying Certbot automatic SSL renewal timer..."
certbot renew --dry-run

echo "✅ Domain and SSL setup successfully completed for https://${DOMAIN}!"
