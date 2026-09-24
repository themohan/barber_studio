# Private Millionaires Barber Studio - Deployment & Operations Guide

This guide covers end-to-end setup and deployment of the real-time **Private Millionaires Barber Studio** web platform.

---

## 1. Quick Local Execution

### Prerequisites
- Python 3.10+
- `pip` and virtual environment support

### Steps
```bash
# 1. Clone or navigate to the project directory
cd barber_studio

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 3. Install production dependencies
pip install -r requirements.txt

# 4. Launch the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
**http://localhost:8000**

Interactive Swagger API Documentation:
**http://localhost:8000/docs**

---

## 2. Docker & Docker Compose Deployment

### Option A: 1-Command Startup with Docker Compose
```bash
docker compose up -d --build
```
This automatically builds the Python container, mounts persistent volumes for SQLite and file uploads, and opens port 8000.

### Option B: Raw Docker
```bash
# Build image
docker build -t private-millionaires-barber .

# Run container
docker run -d -p 8000:8000 \
  -e SECRET_KEY="your-production-secret-key-here" \
  -v $(pwd)/barber_studio.db:/app/barber_studio.db \
  -v $(pwd)/static/images/uploads:/app/static/images/uploads \
  --name pm_barber_app private-millionaires-barber
```

---

## 3. Cloud Deployment Options

### A. Deploy to Render (Recommended for Free / Low-Cost Hosting)
1. Push your repository to GitHub or GitLab.
2. Sign in to [Render.com](https://render.com).
3. Click **New +** -> **Web Service**.
4. Connect your repository.
5. Configure settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables:
   - `SECRET_KEY`: `<Generate a random 32+ character string>`
   - `DATABASE_URL`: `sqlite+aiosqlite:///./barber_studio.db`
7. Click **Deploy Web Service**. Render provides automatic SSL (`https://`) and WebSocket routing.

### B. Deploy to Railway
1. Sign in to [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub Repo**.
3. Select this repository. Railway automatically detects `Dockerfile` or `requirements.txt`.
4. Under **Settings**, add a persistent volume mounted at `/app/data` if you want database persistence across deployments.
5. Set environment variable: `PORT=8000`.

### C. Deploy to Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Authenticate & launch
fly launch --name private-millionaires-barber
fly deploy
```

### D. Production VPS (DigitalOcean / Linode / AWS EC2) with Nginx + Systemd

#### 1. Systemd Service (`/etc/systemd/system/barber.service`)
```ini
[Unit]
Description=Private Millionaires Barber Studio FastAPI Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/barber_studio
Environment="PATH=/var/www/barber_studio/venv/bin"
Environment="SECRET_KEY=production_random_secret_string"
ExecStart=/var/www/barber_studio/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable barber
sudo systemctl start barber
```

#### 2. Nginx Configuration with WebSocket Support (`/etc/nginx/sites-available/barber.conf`)
```nginx
server {
    server_name privatemillionairesbarber.com www.privatemillionairesbarber.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/barber.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
# Enable free Let's Encrypt SSL
sudo certbot --nginx -d privatemillionairesbarber.com -d www.privatemillionairesbarber.com
```

---

## 4. Default Seed Credentials

Out of the box, the application auto-seeds with authentic studio information:

| Role | Email | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Master Barber (Admin)** | `admin@privatemillionaires.com` | `admin123` | Full Studio Management (Release slots, Add/Edit products & services, Appointments & Orders dashboard) |
| **VIP Customer** | `customer@vip.com` | `customer123` | Book slots, Leave reviews, Buy grooming products, Track orders & appointments |

> [!NOTE]
> Change the default admin password upon initial deployment in production.

---

## 5. Studio Information & Verification

- **Business Name**: Private Millionaires Barber Studio
- **Address**: 1740 East Washington Street, Colton, CA 92324
- **Phone**: (909) 430-4591
- **Google Maps**: [View on Google Maps](https://maps.app.goo.gl/F4WUJes6jkD8sakB6)
