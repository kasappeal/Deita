# Deployment Best Practices

## Overview

Deita deployments prioritize reproducibility, security, and operational simplicity. The following practices reflect actual deployment configuration and processes used in the project.

## Deployment Architecture

### Current Deployment Stack

- **Host**: Hetzner Cloud (as per project configuration)
- **Orchestration**: Docker Compose (production-ready)
- **Registry**: GitHub Container Registry (ghcr.io)
- **CI/CD**: GitHub Actions (automated build and test)
- **Monitoring**: Health checks on all services

### Service Topology

```
┌─────────────────────────────────────────┐
│         Internet (HTTPS)                │
└───────────────┬─────────────────────────┘
                │
        ┌───────▼────────┐
        │   Frontend     │
        │ (Nginx:80)     │
        │ Port 3000→80   │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │   Backend      │
        │ (FastAPI:8000) │
        │ Port 8000→8000 │
        └───┬────────┬───┘
            │        │
    ┌───────▼──┐  ┌──▼────────┐
    │PostgreSQL│  │  DuckDB   │
    │ (Port    │  │  (File)   │
    │  5432)   │  │  /app/data│
    └──────────┘  └───────────┘
```

## Containerization

### Backend Dockerfile (Python)

**Location**: `backend/Dockerfile`

**Key Features:**

- **Base Image**: `python:3.12-slim` (minimal attack surface)
- **Non-root User**: `deita:deita` user/group
- **Build Tool**: uv (fast Python package installer)
- **Dependencies**: Only runtime deps (`uv sync --no-dev`)
- **Health Check**: Curl to `/health` endpoint every 30s
- **Working Directory**: `/app`

**Multi-stage Build (Not Implemented Yet):**
Current Dockerfile is single-stage. Could be optimized with multi-stage build:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev

# Stage 2: Runtime
FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
# ... rest of runtime config
```

**Security Hardening:**

- ✅ Non-root user (`USER deita`)
- ✅ No cache directories (`PIP_NO_CACHE_DIR=1`)
- ✅ Minimal system packages (only curl, libmagic1)
- ✅ APT cache cleaned (`rm -rf /var/lib/apt/lists/*`)
- ✅ Health check configured
- ⚠️ Could use distroless base image for even better security

### Frontend Dockerfile (React/Vite)

**Location**: `frontend/Dockerfile`

**Multi-stage Build:**

```dockerfile
# Stage 1: Build (node:20-slim)
FROM node:20-slim AS build
# ... npm ci, npm run build

# Stage 2: Production (nginx:alpine)
FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
```

**Key Features:**

- ✅ Multi-stage build (build → production)
- ✅ Small production image (nginx:alpine)
- ✅ Custom nginx configuration
- ✅ Build-time environment variables (`ARG VITE_API_URL`)
- ✅ Health check (wget to localhost:80)
- ✅ No Node.js in production image

**Security Hardening:**

- ✅ Alpine Linux base (minimal attack surface)
- ✅ Only static files in production
- ✅ nginx runs as non-root by default
- ✅ Health check configured

### .dockerignore Files

**Backend** (`.dockerignore` not present - technical debt):
Should exclude:

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Development
.env
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore
```

**Frontend** (`.dockerignore` not present - technical debt):
Should exclude:

```
node_modules/
dist/
coverage/
.env*
.vscode/
.idea/
*.log
.git/
.gitignore
README.md
```

## Orchestration (Docker Compose)

### Production Configuration

**File**: `docker-compose.yml`

**Services:**

1. **backend**: FastAPI application

   - Image: `ghcr.io/kasappeal/deita/backend:latest`
   - Port: 8000→8000
   - Health check: curl `/v1/health` every 30s
   - Depends on: postgres
   - Restart: unless-stopped
   - Volumes: duckdb_data:/app/data

2. **frontend**: Nginx serving React SPA

   - Image: `ghcr.io/kasappeal/deita/frontend:latest`
   - Port: 3000→80
   - Health check: curl localhost:80 every 30s
   - Depends on: backend
   - Restart: unless-stopped

3. **postgres**: PostgreSQL database
   - Image: `postgres:15-alpine`
   - Port: 5432→5432
   - Health check: pg_isready every 10s
   - Restart: unless-stopped
   - Volumes: postgres_data:/var/lib/postgresql/data

**Volume Management:**

```yaml
volumes:
  postgres_data:
    driver: local
  duckdb_data:
    driver: local
```

**Network Configuration:**

```yaml
networks:
  default:
    name: deita-network
```

### Development Configuration

**File**: `docker-compose.dev.yml`

**Additional Services:**

- **minio**: S3-compatible object storage (dev only)
- **mailhog**: Email testing (dev only)

**Key Differences from Production:**

- Backend mounts source code as volume for hot reload
- Frontend uses Vite dev server (not nginx)
- DEBUG=true environment variable
- Additional development tools exposed

### Resource Limits (Not Configured - Technical Debt)

Should add to production `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 512M
```

## CI/CD Pipeline (GitHub Actions)

### Automated Workflows

**Location**: `.github/workflows/` (not visible in current workspace)

**Expected Workflows:**

1. **Test & Lint** (on every PR and push):

```yaml
name: Test & Lint
on: [push, pull_request]
jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          uv sync
          uv run pytest --cov=app
      - name: Run backend lint
        run: |
          cd backend
          uv run ruff check .

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm test
      - name: Run frontend lint
        run: |
          cd frontend
          npm run lint
```

2. **Build & Push** (on main branch):

```yaml
name: Build & Push
on:
  push:
    branches: [main]
jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push backend
        run: |
          docker build -t ghcr.io/kasappeal/deita/backend:latest backend/
          docker push ghcr.io/kasappeal/deita/backend:latest

  build-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push frontend
        run: |
          docker build -t ghcr.io/kasappeal/deita/frontend:latest frontend/
          docker push ghcr.io/kasappeal/deita/frontend:latest
```

3. **Deploy** (manual trigger):

```yaml
name: Deploy
on:
  workflow_dispatch:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: SSH and deploy
        run: |
          ssh user@server 'cd /opt/deita && docker-compose pull && docker-compose up -d'
```

### Image Versioning Strategy

**Current**: Latest tag only
**Recommended**: Semantic versioning

```bash
# Tag with version and latest
docker tag ghcr.io/kasappeal/deita/backend:latest ghcr.io/kasappeal/deita/backend:v1.2.3
docker push ghcr.io/kasappeal/deita/backend:v1.2.3
docker push ghcr.io/kasappeal/deita/backend:latest
```

## Secrets & Configuration Management

### Environment Variables (Production)

**File**: `.env` (not committed to repo)

**Required Variables:**

```bash
# Database
POSTGRES_PASSWORD=<strong-random-password>

# S3 Storage (production)
S3_ENDPOINT=https://s3.eu-central-1.amazonaws.com
S3_ACCESS_KEY=<aws-access-key>
S3_SECRET_KEY=<aws-secret-key>
S3_BUCKET_NAME=deita-production-files

# Email Service (production)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@deita.app

# Security
SECRET_KEY=<64-char-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME=Deita
APP_VERSION=1.0.0

# DuckDB
DUCKDB_PATH=/app/data/deita.duckdb

# AI Model
AI_MODEL_NAME=anthropic/claude-3-haiku-20240307
AI_MODEL_ENDPOINT=https://openrouter.ai/api/v1
AI_MODEL_API_KEY=<openrouter-api-key>
```

### Secret Rotation Best Practices

**Not Yet Implemented (Technical Debt):**

- Automated secret rotation schedule
- Secret versioning in vault
- Audit trail for secret access

**Current Process:**

1. Generate new secret
2. Update `.env` file on server
3. Restart affected services: `docker-compose restart backend`

### Docker Secrets (Not Used - Technical Debt)

**Recommended for Production:**

```yaml
services:
  backend:
    secrets:
      - postgres_password
      - secret_key
      - ai_api_key
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password

secrets:
  postgres_password:
    external: true
  secret_key:
    external: true
  ai_api_key:
    external: true
```

## Monitoring & Logging

### Health Checks

**Backend** (`/v1/health`):

```python
@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "deita-backend"}
```

**Docker Health Checks:**

- Backend: curl http://localhost:8000/v1/health every 30s
- Frontend: wget http://localhost:80 every 30s
- Postgres: pg_isready every 10s

### Logging Strategy

**Backend:**

- Python logging to stdout/stderr
- Log level: INFO (production), DEBUG (dev)
- Structured logging: JSON format recommended (not yet implemented)
- Log aggregation: Not configured (technical debt)

**Frontend:**

- Nginx access logs to stdout
- Nginx error logs to stderr
- Browser console errors (not collected)

**Not Yet Implemented (Technical Debt):**

- Centralized logging (ELK Stack, Loki, CloudWatch)
- Log retention policies
- Log-based alerting
- Request tracing across services

### Analytics & Monitoring

**Posthog Integration**: Mentioned in PRD but NOT implemented (technical debt)

**Should Track:**

- API endpoint latency
- Query execution time
- File upload success/failure rates
- User authentication events
- Workspace creation/deletion
- Storage usage per workspace

**Recommended Tools:**

- **Application Monitoring**: Sentry (error tracking)
- **Infrastructure Monitoring**: Prometheus + Grafana
- **Uptime Monitoring**: UptimeRobot or Pingdom

## Security Best Practices

### TLS/HTTPS Configuration

**Not Configured in Current Setup (Technical Debt):**

**Recommended Setup (Nginx Reverse Proxy):**

```nginx
server {
    listen 443 ssl http2;
    server_name deita.app;

    ssl_certificate /etc/letsencrypt/live/deita.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/deita.app/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /v1/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name deita.app;
    return 301 https://$server_name$request_uri;
}
```

### Image Vulnerability Scanning

**Not Yet Implemented (Technical Debt):**

**Recommended Tools:**

- **Trivy**: `trivy image ghcr.io/kasappeal/deita/backend:latest`
- **Hadolint**: `hadolint backend/Dockerfile`
- **Snyk**: Container scanning in CI/CD

**CI Integration:**

```yaml
- name: Scan image for vulnerabilities
  run: |
    trivy image --exit-code 1 --severity HIGH,CRITICAL ghcr.io/kasappeal/deita/backend:latest
```

### Security Headers (Frontend nginx.conf)

**Should Include:**

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
```

## Backup & Recovery

### Database Backups

**Not Yet Implemented (Technical Debt):**

**Recommended Strategy:**

```bash
# Automated daily backups
0 2 * * * docker exec deita-postgres pg_dump -U deita deita | gzip > /backups/deita-$(date +\%Y\%m\%d).sql.gz

# Retention: 7 daily, 4 weekly, 12 monthly
```

**Restoration:**

```bash
# Restore from backup
gunzip -c /backups/deita-20250114.sql.gz | docker exec -i deita-postgres psql -U deita deita
```

### Object Storage Backups

**S3 Versioning:**

- Enable S3 bucket versioning for file recovery
- Lifecycle policies for old versions (30 days)

**Not Yet Configured (Technical Debt):**

- Cross-region replication
- Backup to separate storage account

### DuckDB Backups

**Current State:**

- DuckDB file stored in Docker volume `duckdb_data`
- Not backed up automatically

**Recommended:**

```bash
# Backup DuckDB file
docker cp deita-backend:/app/data/deita.duckdb /backups/deita-duckdb-$(date +\%Y\%m\%d).duckdb
```

### Disaster Recovery Plan

**Not Yet Documented (Technical Debt):**

**Should Include:**

1. **Recovery Time Objective (RTO)**: Target recovery time (e.g., 4 hours)
2. **Recovery Point Objective (RPO)**: Acceptable data loss (e.g., 24 hours)
3. **Runbook**: Step-by-step recovery procedures
4. **Contact List**: On-call engineers and escalation path
5. **Testing Schedule**: Quarterly disaster recovery drills

## Deployment Procedures

### Initial Deployment (Production)

```bash
# 1. Provision server (Hetzner Cloud)
hcloud server create --name deita-prod --type cx21 --image ubuntu-22.04

# 2. SSH into server
ssh root@<server-ip>

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Clone repository
git clone https://github.com/kasappeal/deita.git /opt/deita
cd /opt/deita

# 5. Create .env file
cp .env.example .env
nano .env  # Edit with production values

# 6. Pull images
docker-compose pull

# 7. Initialize database
docker-compose up -d postgres
docker-compose run backend uv run alembic upgrade head

# 8. Start all services
docker-compose up -d

# 9. Verify health
curl http://localhost:8000/v1/health
curl http://localhost:3000
```

### Rolling Updates (Zero-Downtime)

**Current Process (Manual):**

```bash
# 1. Pull latest images
docker-compose pull

# 2. Recreate services
docker-compose up -d

# Docker Compose automatically:
# - Starts new containers
# - Waits for health checks
# - Stops old containers
```

**Not Yet Implemented:**

- Blue-green deployment
- Canary releases
- Automated rollback on failure

### Rollback Procedure

```bash
# 1. Identify previous working version
docker images | grep ghcr.io/kasappeal/deita

# 2. Update docker-compose.yml to specific version
# Change: image: ghcr.io/kasappeal/deita/backend:latest
# To:     image: ghcr.io/kasappeal/deita/backend:v1.2.2

# 3. Pull and restart
docker-compose pull
docker-compose up -d

# 4. Verify rollback
curl http://localhost:8000/v1/health
```

### Database Migrations

```bash
# 1. Backup database before migration
docker exec deita-postgres pg_dump -U deita deita > pre-migration-backup.sql

# 2. Run migrations
docker-compose run backend uv run alembic upgrade head

# 3. Verify migration
docker-compose run backend uv run alembic current

# 4. If migration fails, rollback
docker-compose run backend uv run alembic downgrade -1
```

## Production Readiness Checklist

### Infrastructure

- [ ] TLS/HTTPS configured with valid certificate
- [ ] Reverse proxy (nginx) in front of services
- [ ] Firewall rules configured (only 80, 443 exposed)
- [ ] SSH key-based authentication only
- [ ] Regular OS security updates scheduled
- [ ] Dedicated server or VM (not shared hosting)

### Application

- [x] Environment variables configured (no hardcoded secrets)
- [x] DEBUG=false in production
- [x] Rate limiting enabled (SlowAPI)
- [x] Health checks on all services
- [ ] Error tracking configured (Sentry)
- [ ] Logging aggregation configured
- [ ] Metrics and monitoring configured

### Security

- [x] Non-root users in containers
- [ ] TLS/HTTPS enforced
- [ ] Security headers configured (CSP, X-Frame-Options)
- [ ] Image vulnerability scanning in CI
- [ ] Secrets rotation schedule defined
- [x] SQL injection prevention (parameterized queries)
- [x] CORS configured correctly
- [x] JWT authentication implemented

### Data

- [ ] Automated database backups (daily)
- [ ] Backup restoration tested
- [ ] S3 bucket versioning enabled
- [ ] Data retention policies defined
- [ ] GDPR/data privacy compliance reviewed

### Operations

- [ ] Deployment runbook documented
- [ ] Rollback procedure documented
- [ ] Disaster recovery plan documented
- [ ] On-call rotation defined
- [ ] Incident response process defined
- [ ] Uptime monitoring configured
- [ ] Alerting rules configured

### Documentation

- [x] README with getting started instructions
- [x] API documentation (OpenAPI)
- [x] Architecture diagrams up to date
- [x] Deployment procedures documented (this file)
- [ ] Runbooks for common operations
- [ ] Troubleshooting guide

## Extensibility & Future Scaling

### Migration to Kubernetes (When Needed)

**Triggers:**

- > 100 concurrent users
- Need for auto-scaling
- Multi-region deployment required
- Managed services preferred

**Migration Path:**

1. Convert Docker Compose to Kubernetes manifests (Kompose)
2. Set up managed Kubernetes (GKE, EKS, AKS)
3. Migrate to managed PostgreSQL (Cloud SQL, RDS)
4. Implement Horizontal Pod Autoscaling
5. Set up Ingress controller (nginx-ingress)
6. Configure persistent volume claims
7. Implement CI/CD for Kubernetes (ArgoCD, Flux)

### Cloud-Native Services

**AWS Equivalent:**

- EC2 → ECS Fargate (serverless containers)
- Docker Compose → ECS Task Definitions
- PostgreSQL → RDS PostgreSQL
- MinIO → S3
- DuckDB → Athena or Redshift Serverless

**GCP Equivalent:**

- Compute Engine → Cloud Run (serverless containers)
- Docker Compose → Cloud Compose or GKE
- PostgreSQL → Cloud SQL
- MinIO → Cloud Storage
- DuckDB → BigQuery

### Multi-Region Deployment

**When Needed:**

- Global user base
- Low-latency requirements
- High availability requirements

**Architecture:**

- Deploy backend in multiple regions
- Use global load balancer (CloudFront, Cloud CDN)
- Replicate PostgreSQL across regions
- Shared S3 bucket or cross-region replication
- Redis for distributed caching and session management
