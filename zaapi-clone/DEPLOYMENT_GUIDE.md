# Deployment Guide - Zaapi Clone

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git repository initialized

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Setup
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://api.zaapi.com
NEXT_PUBLIC_APP_URL=https://app.zaapi.com
NODE_ENV=production
```

### 3. Development
```bash
npm run dev
# Open http://localhost:3000
```

### 4. Production Build
```bash
npm run build
npm start
```

## Deployment Options

### Option A: Vercel (Recommended)
```bash
npm i -g vercel
vercel login
vercel --prod
```

**Vercel Configuration:**
- Framework Preset: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`
- Node Version: 18.x

### Option B: Docker
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t zaapi-clone .
docker run -p 3000:3000 -e NODE_ENV=production zaapi-clone
```

### Option C: Traditional Server
```bash
# Build on local machine
npm run build

# Upload to server
scp -r .next public package.json user@server:/var/www/zaapi-clone

# On server
cd /var/www/zaapi-clone
npm install --only=production
pm2 start npm --name "zaapi-clone" -- start
```

### Option D: Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zaapi-clone
spec:
  replicas: 3
  selector:
    matchLabels:
      app: zaapi-clone
  template:
    metadata:
      labels:
        app: zaapi-clone
    spec:
      containers:
      - name: zaapi-clone
        image: your-registry/zaapi-clone:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: zaapi-clone-service
spec:
  selector:
    app: zaapi-clone
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

## Performance Optimization

### 1. Enable Compression
Install compression middleware:
```bash
npm install compression
```

Add to `src/middleware.ts`:
```typescript
import compression from 'compression';
```

### 2. CDN Configuration
Configure CDN for static assets:
- `/images/*` → Cache for 1 year
- `/_next/static/*` → Cache for 1 year
- HTML pages → No cache or short cache

### 3. Database Optimization
For production, connect to:
- PostgreSQL for primary data
- Redis for caching and sessions
- Elasticsearch for search functionality

## Monitoring & Logging

### Health Check Endpoint
Access at: `/api/health`

### Metrics to Monitor
- Response time (< 200ms average)
- Error rate (< 0.1%)
- Active connections
- Memory usage (< 512MB)
- CPU usage (< 70%)

### Logging Setup
```bash
npm install winston @types/winston
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] CORS properly set
- [ ] Rate limiting enabled
- [ ] Input validation active
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] Environment variables secured
- [ ] Regular dependency updates

## Scaling Strategy

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use sticky sessions for WebSocket connections
- Implement distributed caching (Redis Cluster)

### Vertical Scaling
- Increase Node.js memory: `NODE_OPTIONS="--max-old-space-size=4096"`
- Upgrade server resources
- Optimize database queries

## Backup & Recovery

### Daily Backups
```bash
# Database backup
pg_dump zaapi_db > backup_$(date +%Y%m%d).sql

# Asset backup
tar -czf assets_backup.tar.gz public/
```

### Disaster Recovery
1. Restore database from backup
2. Redeploy application
3. Verify health checks
4. Update DNS if needed

## Troubleshooting

### Common Issues

**Build fails:**
```bash
rm -rf node_modules .next
npm install
npm run build
```

**Memory issues:**
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
```

**Port already in use:**
```bash
lsof -ti:3000 | xargs kill
```

## Support

For production issues, contact your DevOps team or refer to:
- Next.js Documentation: https://nextjs.org/docs
- Vercel Deployment: https://vercel.com/docs
- Docker Docs: https://docs.docker.com

---

Last Updated: 2024
Version: 1.0.0
