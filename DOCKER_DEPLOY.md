# Docker Deployment Guide

Deploy the Job Server API using Docker for easy, consistent deployment.

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

API available at: **http://localhost:8000**

### Option 2: Docker Only

```bash
# Build image
docker build -t job-server-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  --name job-api \
  job-server-api

# View logs
docker logs -f job-api

# Stop
docker stop job-api
docker rm job-api
```

---

## Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=sqlite:////app/data/job_board.db

# RapidAPI (optional)
RAPIDAPI_KEY=your_key_here
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Production Deployment

### With Nginx Reverse Proxy

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  job-server:
    build: .
    expose:
      - "8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:////app/data/job_board.db
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - job-server
    restart: always
```

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://job-server:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Docker Commands

### Build
```bash
docker build -t job-server-api .
```

### Run
```bash
docker run -d \
  -p 8000:8000 \
  --name job-api \
  job-server-api
```

### Logs
```bash
# Follow logs
docker logs -f job-api

# Last 100 lines
docker logs --tail 100 job-api
```

### Shell Access
```bash
docker exec -it job-api /bin/bash
```

### Stop/Start
```bash
docker stop job-api
docker start job-api
docker restart job-api
```

### Remove
```bash
docker stop job-api
docker rm job-api
```

---

## Data Persistence

### Volumes

Data is persisted in the `./data` directory:

```
data/
├── job_board.db     # Job board database
└── jobs.db          # Full aggregator database
```

### Backup

```bash
# Backup databases
docker exec job-api tar -czf /tmp/backup.tar.gz /app/data
docker cp job-api:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# Restore
docker cp backup.tar.gz job-api:/tmp/backup.tar.gz
docker exec job-api tar -xzf /tmp/backup.tar.gz -C /
```

---

## Monitoring

### Health Check

```bash
# Check if container is healthy
docker ps

# Manual health check
curl http://localhost:8000/health
```

### Resource Usage

```bash
# CPU and memory usage
docker stats job-api

# Detailed info
docker inspect job-api
```

---

## Scaling

### Multiple Instances

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  job-server:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/jobs
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - job-server

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=jobs
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# Scale to 3 instances
docker-compose -f docker-compose.scale.yml up -d --scale job-server=3
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs job-api

# Check if port is in use
netstat -an | grep 8000

# Remove and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues

```bash
# Access database
docker exec -it job-api sqlite3 /app/data/job_board.db

# Check tables
.tables

# Check data
SELECT COUNT(*) FROM job_listings;
```

### Permission Issues

```bash
# Fix permissions
chmod -R 755 data/
```

---

## CI/CD Integration

### GitHub Actions

```.yaml
# .github/workflows/docker.yml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t job-server-api .

      - name: Run tests
        run: docker run job-server-api pytest

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag job-server-api username/job-server-api:latest
          docker push username/job-server-api:latest
```

---

## Security

### Best Practices

1. **Use environment variables** for secrets
2. **Don't expose unnecessary ports**
3. **Run as non-root user**
4. **Keep base image updated**
5. **Scan for vulnerabilities**

```bash
# Scan image for vulnerabilities
docker scan job-server-api
```

### Improved Dockerfile (Security)

```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "job_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Next Steps

1. **Test locally**: `docker-compose up`
2. **Check API**: Visit http://localhost:8000/docs
3. **Deploy to production**: Use docker-compose.prod.yml
4. **Set up monitoring**: Add logging and metrics
5. **Configure backups**: Schedule regular database backups

**Ready to deploy!** 🚀
