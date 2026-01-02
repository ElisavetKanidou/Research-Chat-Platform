# 🐳 Docker Deployment Guide

Οδηγίες για deployment του Research Chat AI με Docker.

## 📋 Προαπαιτούμενα

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ RAM διαθέσιμα
- 10GB+ disk space

## 🚀 Quick Start

### 1. Clone & Configure

```bash
# Clone το repository (αν δεν το έχεις ήδη)
git clone <your-repo-url>
cd research-chat-ai

# Δημιούργησε .env file από το template
cp .env.production.example .env

# Επεξεργάσου το .env με τα API keys σου
nano .env  # ή vim, code, κτλ
```

### 2. Σημαντικές Ρυθμίσεις στο .env

**ΑΠΑΡΑΙΤΗΤΑ:**
```env
# Άλλαξε σε strong password
POSTGRES_PASSWORD=your_strong_password_here

# Άλλαξε σε random secret key (min 32 chars)
SECRET_KEY=your_random_secret_key_at_least_32_characters_long

# Πρόσθεσε τα AI API keys που χρειάζεσαι
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
GPT_OSS_API_KEY=your_key
GPT_OSS_BASE_URL=http://your-server:port/v1
```

**ΓΙΑ PRODUCTION:**
```env
# Άλλαξε τα URLs για production domain
FRONTEND_URL=https://yourdomain.com
VITE_API_URL=https://yourdomain.com/api/v1
CORS_ORIGINS=https://yourdomain.com
```

### 3. Build & Run

```bash
# Build όλα τα containers
docker-compose build

# Start όλα τα services
docker-compose up -d

# Δες τα logs
docker-compose logs -f

# Έλεγξε το status
docker-compose ps
```

### 4. Verify Deployment

```bash
# Backend health check
curl http://localhost:8080/api/v1/health

# Frontend
open http://localhost:3000

# Database connection
docker-compose exec backend python -c "from app.core.database import test_connection; test_connection()"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Nginx (Port 3000)               │
│         Frontend (React/Vite)           │
└─────────────┬───────────────────────────┘
              │
              │ HTTP Requests
              ▼
┌─────────────────────────────────────────┐
│    FastAPI Backend (Port 8080)          │
│    - REST API                           │
│    - AI Integration                     │
│    - Authentication                     │
└─────────────┬───────────────────────────┘
              │
              │ SQL Queries
              ▼
┌─────────────────────────────────────────┐
│    PostgreSQL (Port 5432)               │
│    - Internal network only              │
│    - Persistent volume                  │
└─────────────────────────────────────────┘
```

## 📦 Services

### Frontend (Port 3000)
- React app served by Nginx
- Production build με optimizations
- Health check: `http://localhost:3000/health`

### Backend (Port 8080)
- FastAPI with 4 Uvicorn workers
- Health check: `http://localhost:8080/api/v1/health`
- Depends on: PostgreSQL

### Database (Internal only)
- PostgreSQL 15
- Data persisted in Docker volume
- Auto-backup recommended

## 🔧 Common Commands

### Start/Stop
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart backend
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database
```bash
# Access PostgreSQL CLI
docker-compose exec db psql -U postgres -d research_chat

# Backup database
docker-compose exec db pg_dump -U postgres research_chat > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres research_chat
```

### Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## 🔒 Security Checklist

- [ ] Changed `POSTGRES_PASSWORD` to strong password
- [ ] Changed `SECRET_KEY` to random 32+ character string
- [ ] Set proper `CORS_ORIGINS` for production
- [ ] All API keys are in `.env` file (not committed to git)
- [ ] `.env` file has restricted permissions: `chmod 600 .env`
- [ ] Database port NOT exposed to host in production
- [ ] Using HTTPS in production (reverse proxy/load balancer)
- [ ] Regular database backups configured

## 🌐 Production Deployment

### Using Reverse Proxy (Recommended)

Add Nginx/Traefik/Caddy in front for:
- HTTPS/SSL termination
- Domain routing
- Rate limiting
- Load balancing

Example Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment-Specific Ports

Αν χρειάζεσαι διαφορετικές θύρες, άλλαξε στο docker-compose.yml:

```yaml
frontend:
  ports:
    - "3001:3000"  # Host:Container

backend:
  ports:
    - "8081:8080"
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Βρες ποια διεργασία χρησιμοποιεί τη θύρα
sudo lsof -i :3000
sudo lsof -i :8080

# Άλλαξε τις θύρες στο docker-compose.yml
```

### Database Connection Failed
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify credentials
docker-compose exec db psql -U postgres -d research_chat
```

### Frontend Can't Connect to Backend
```bash
# Check VITE_API_URL in .env
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Out of Memory
```bash
# Check resource usage
docker stats

# Reduce Uvicorn workers in backend/Dockerfile
# Change --workers 4 to --workers 2
```

## 📊 Monitoring

### Health Checks
```bash
# All services status
docker-compose ps

# Backend health
curl http://localhost:8080/api/v1/health

# Frontend health
curl http://localhost:3000/health

# Database
docker-compose exec db pg_isready -U postgres
```

### Resource Usage
```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Clean up
docker system prune -a
```

## 🔄 Backup & Restore

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T db pg_dump -U postgres research_chat > \
  "$BACKUP_DIR/db_backup_$DATE.sql"

# Uploads backup
docker run --rm -v research-chat-ai_uploads:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/uploads_$DATE.tar.gz -C /data .

echo "Backup completed: $DATE"
```

### Restore
```bash
# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres research_chat

# Restore uploads
docker run --rm -v research-chat-ai_uploads:/data -v $(pwd):/backup \
  alpine tar xzf /backup/uploads_backup.tar.gz -C /data
```

## 📞 Support

Για βοήθεια:
1. Check logs: `docker-compose logs -f`
2. Verify .env configuration
3. Check GitHub issues
4. Review INTEGRATION_SETUP_GUIDE.md

---

**Ports Used:**
- Frontend: 3000
- Backend: 8080
- Database: 5432 (internal only)

**Data Persistence:**
- PostgreSQL data: `postgres_data` volume
- Uploaded files: `./backend/uploads` bind mount
