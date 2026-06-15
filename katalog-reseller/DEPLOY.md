# 🚀 Deployment Guide — Katalog Reseller VPS

Panduan lengkap deploy aplikasi **Katalog Reseller** ke VPS production.

---

## 📋 Prasyarat VPS

| Komponen | Minimal | Rekomendasi |
|----------|---------|-------------|
| **OS** | Ubuntu 20.04 / 22.04 / 24.04 | Ubuntu 24.04 LTS |
| **CPU** | 1 Core | 2 Core |
| **RAM** | 1 GB | 2 GB |
| **Disk** | 10 GB | 20 GB SSD |
| **Docker** | 24+ | Latest |
| **Domain** | Optional | Untuk SSL |

---

## ⚡ Quick Deploy (Docker)

```bash
# 1. Clone / upload project ke VPS
cd /opt
git clone <repo-url> katalog-reseller
# atau: scp -r KATALOG\ RESELLER/ user@vps:/opt/katalog-reseller/

cd /opt/katalog-reseller

# 2. Jalankan deploy script
chmod +x deploy.sh
sudo DOMAIN=reseller.example.com EMAIL=admin@example.com ./deploy.sh
```

---

## 🐳 Manual Docker Deploy

### Step 1: Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Logout & login ulang
```

### Step 2: Build & Run

```bash
cd /opt/katalog-reseller

# Build image
docker build -t katalog-reseller .

# Run container
docker run -d \
  --name katalog-reseller \
  --restart unless-stopped \
  -p 8501:8501 \
  -v $(pwd)/static/uploads:/app/static/uploads \
  katalog-reseller
```

### Step 3: Verify

```bash
curl http://localhost:8501/_stcore/health
# Output: ok
```

Aplikasi dapat diakses di **http://VPS_IP:8501**

---

## 🐳 Docker Compose (Recommended)

```bash
# Basic (Streamlit only)
docker compose up -d app

# With Nginx + SSL (production)
docker compose --profile production up -d
```

---

## 🔒 SSL dengan Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot

# Generate certificate
sudo certbot certonly --standalone -d reseller.example.com

# Copy ke Nginx certs
sudo cp /etc/letsencrypt/live/reseller.example.com/fullchain.pem nginx/certs/
sudo cp /etc/letsencrypt/live/reseller.example.com/privkey.pem nginx/certs/

# Start Nginx
docker compose --profile production up -d nginx

# Auto-renewal (cron)
echo "0 3 * * * certbot renew --quiet && docker compose -f /opt/katalog-reseller/docker-compose.yml restart nginx" | sudo crontab -
```

---

## 🔄 Systemd Service (Auto-start)

```bash
# Copy service file
sudo cp katalog-reseller.service /etc/systemd/system/

# Enable & start
sudo systemctl daemon-reload
sudo systemctl enable katalog-reseller
sudo systemctl start katalog-reseller

# Check status
sudo systemctl status katalog-reseller
```

---

## 🛠️ Environment Variables

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `STREAMLIT_SERVER_PORT` | `8501` | Port aplikasi |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Mode headless |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Bind address |

---

## 🔧 Maintenance Commands

```bash
# Lihat logs
docker logs -f katalog-reseller

# Restart
docker compose restart app

# Update aplikasi
docker compose down
git pull
docker compose up -d --build app

# Cleanup
docker system prune -af
```

---

## ⚠️ Production Notes

### 🔐 Keamanan
- **Ganti password default!** Edit `utils/auth.py` → `USERS` dict
- Gunakan **firewall**: `sudo ufw allow 80,443,8501/tcp`
- Aktifkan **SSL** untuk production (wajib!)
- Jangan expose port 8501 langsung ke internet — gunakan Nginx reverse proxy

### 📦 Data Persistence
- Saat ini data disimpan di **`st.session_state`** (ephemeral/session-based)
- **Untuk production**, upgrade ke database:
  - **Supabase** (PostgreSQL + Auth gratis)
  - **MongoDB Atlas** (NoSQL, free tier)
  - **SQLite + file mount** (simpel, untuk low-traffic)

### 🔄 Backup
```bash
# Backup volume uploads
tar -czf backup-$(date +%Y%m%d).tar.gz static/uploads/

# Restore
tar -xzf backup-20260113.tar.gz
```

---

## 📊 Monitoring

```bash
# Resource usage
docker stats katalog-reseller

# Health check
curl http://localhost:8501/_stcore/health

# Setup Uptime Kuma (opsional)
# docker run -d --name uptime-kuma -p 3001:3001 louislam/uptime-kuma
```

---

## 🆘 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Port 8501 already in use | `sudo lsof -i :8501` → kill proses |
| Container restart terus | `docker logs katalog-reseller` → cek error |
| Upload gambar gagal | Cek `maxUploadSize` di `.streamlit/config.toml` |
| WebSocket error | Pastikan Nginx config punya `proxy_set_header Upgrade` |

---

> **© Katalog Reseller v1.0** — Production-ready Streamlit PWA
