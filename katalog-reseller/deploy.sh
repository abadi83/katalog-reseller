#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# KATALOG RESELLER — VPS Deployment Script
# ═══════════════════════════════════════════════════════════════
set -e

APP_DIR="/opt/katalog-reseller"
DOMAIN="${DOMAIN:-reseller.example.com}"
EMAIL="${EMAIL:-admin@example.com}"

echo "🚀 Deploying Katalog Reseller..."

# ── 1. Install Docker (Ubuntu/Debian) ──
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
fi

# ── 2. Clone / Copy App ──
echo "📁 Setting up app at $APP_DIR..."
sudo mkdir -p "$APP_DIR"
sudo cp -r . "$APP_DIR"
sudo chown -R $USER:$USER "$APP_DIR"
cd "$APP_DIR"

# ── 3. Start with Docker Compose ──
echo "🐳 Building & starting containers..."
docker compose up -d --build app

# ── 4. Wait for health check ──
echo "⏳ Waiting for app to be healthy..."
for i in {1..30}; do
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "✅ App is healthy!"
        break
    fi
    sleep 2
done

# ── 5. Setup SSL with Certbot ──
read -p "🔒 Setup SSL with Let's Encrypt? (y/n): " SETUP_SSL
if [ "$SETUP_SSL" = "y" ]; then
    sudo apt-get install -y certbot
    sudo certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/certs/fullchain.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/certs/privkey.pem

    echo "🔒 Starting Nginx with SSL..."
    docker compose --profile production up -d nginx

    # Auto-renewal cron
    echo "0 3 * * * certbot renew --quiet && docker compose restart nginx" | sudo crontab -
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Deployment complete!"
echo "   App:  http://localhost:8501"
if [ "$SETUP_SSL" = "y" ]; then
    echo "   SSL:  https://$DOMAIN"
fi
echo "═══════════════════════════════════════════════════════════"
