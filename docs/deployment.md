# Deployment Guide

## Overview

This guide covers deploying the Real Estate AI Analysis Platform in various environments.

## Deployment Options

1. Docker Compose (Development/Testing)
2. Kubernetes (Production)
3. Cloud Provider (AWS/GCP/Azure)

## Prerequisites

- Docker and Docker Compose
- Kubernetes CLI (kubectl)
- Cloud provider CLI
- SSL certificates
- Environment configurations

## Configuration

### Environment Variables

Create environment files for each environment:

```bash
# .env.production
REDIS_URL=redis://redis:6379
POSTGRES_URL=postgresql://user:pass@db:5432/wholesale
API_KEY=your-api-key
JWT_SECRET=your-jwt-secret
```

### Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  api-gateway:
    build: 
      context: .
      dockerfile: docker/api-gateway/Dockerfile
    environment:
      - NODE_ENV=production
    ports:
      - "443:443"
    depends_on:
      - redis
      - postgres

  market-analysis:
    build:
      context: .
      dockerfile: docker/market-analysis/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  voice-interface:
    build:
      context: .
      dockerfile: docker/voice-interface/Dockerfile
    ports:
      - "8443:8443"

  redis:
    image: redis:6.2-alpine
    volumes:
      - redis-data:/data

  postgres:
    image: postgres:13-alpine
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=wholesale

volumes:
  redis-data:
  postgres-data:
```

### Kubernetes

```yaml
# k8s/api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: wholesale/api-gateway:latest
        ports:
        - containerPort: 443
        env:
        - name: NODE_ENV
          value: production
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Deployment Steps

### 1. Local Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Production (Docker Compose)

```bash
# Build and start services
docker-compose -f docker-compose.production.yml up -d --build

# Check service health
docker-compose ps
docker-compose logs -f

# Update services
docker-compose pull
docker-compose up -d
```

### 3. Production (Kubernetes)

```bash
# Apply configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=api-gateway

# Scale services
kubectl scale deployment api-gateway --replicas=5
```

### 4. Cloud Deployment (AWS)

```bash
# Configure AWS CLI
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name wholesale

# Push images to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin
docker push $AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/wholesale:latest

# Deploy services
aws ecs update-service --cluster wholesale --service api-gateway --force-new-deployment
```

## Monitoring

### 1. Health Checks

```bash
# Check API Gateway
curl -k https://localhost/health

# Check Redis
redis-cli ping

# Check PostgreSQL
psql -h localhost -U user -d wholesale -c "SELECT 1"
```

### 2. Logging

```bash
# View service logs
tail -f /var/log/wholesale/*.log

# View Docker logs
docker-compose logs -f service-name

# View Kubernetes logs
kubectl logs -f deployment/api-gateway
```

### 3. Metrics

```bash
# Check resource usage
docker stats

# View Kubernetes metrics
kubectl top pods
kubectl top nodes
```

## Backup and Recovery

### 1. Database Backup

```bash
# Backup PostgreSQL
pg_dump -h localhost -U user wholesale > backup.sql

# Backup Redis
redis-cli save
```

### 2. Recovery

```bash
# Restore PostgreSQL
psql -h localhost -U user wholesale < backup.sql

# Restore Redis
cp dump.rdb /var/lib/redis/
```

## Security

### 1. SSL Configuration

```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem

# Configure Nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/cert.pem;
    ssl_certificate_key /etc/nginx/key.pem;
}
```

### 2. Firewall Rules

```bash
# Allow HTTPS
ufw allow 443/tcp

# Allow PostgreSQL
ufw allow 5432/tcp

# Allow Redis (internal only)
ufw allow from 10.0.0.0/8 to any port 6379
```

## Troubleshooting

### Common Issues

1. Service won't start:
```bash
# Check logs
docker-compose logs service-name

# Check configuration
docker-compose config

# Verify environment variables
docker-compose run service-name env
```

2. Database connection issues:
```bash
# Check connectivity
nc -zv database-host 5432

# Check credentials
psql -h database-host -U user -d wholesale
```

3. Performance issues:
```bash
# Check resource usage
top
docker stats

# Check slow queries
tail -f /var/log/postgresql/postgresql-slow.log
```

## Rollback Procedures

### 1. Docker Rollback

```bash
# Roll back to previous version
docker-compose pull previous-version
docker-compose up -d
```

### 2. Kubernetes Rollback

```bash
# Roll back deployment
kubectl rollout undo deployment/api-gateway

# Verify rollback
kubectl rollout status deployment/api-gateway
```

## Maintenance

### 1. Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 2. Cleanup

```bash
# Remove unused images
docker image prune -a

# Clean up volumes
docker volume prune

# Clean up logs
find /var/log/wholesale -name "*.log" -mtime +30 -delete
```
