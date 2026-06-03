# Deployment Guide

This guide covers deploying the CBB Stats application to production.

## Architecture

- **Frontend**: Next.js 14 (React)
- **Backend**: FastAPI (Python)
- **Data**: CSV files stored locally

## Deployment Options

### Option 1: Vercel (Frontend) + Render (Backend) - Recommended

**Pros**: Easy setup, free tiers available, good for MVP
**Cons**: May hit limits on free tiers, data file size constraints

#### Frontend (Vercel)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   cd frontend
   vercel
   ```

3. **Configure Environment Variables in Vercel Dashboard**
   - Go to Project Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.onrender.com`

4. **Update `next.config.js` for production**
   ```javascript
   const nextConfig = {
     reactStrictMode: true,
     // Remove rewrites for production (API calls will go directly to backend)
     // async rewrites() {
     //   return [
     //     {
     //       source: '/api/:path*',
     //       destination: 'http://localhost:8000/api/:path*',
     //     },
     //   ]
     // },
   };
   ```

#### Backend (Render)

1. **Create `render.yaml` in backend directory**
   ```yaml
   services:
     - type: web
       name: jeevs-cbb-api
       runtime: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PORT
           value: 8000
         - key: CORS_ORIGINS
           value: '["https://your-frontend-url.vercel.app"]'
   ```

2. **Push to GitHub and connect to Render**
   - Create a GitHub repository
   - Connect Render to your GitHub repo
   - Render will auto-deploy on push

3. **Configure Environment Variables in Render Dashboard**
   - `HOST`: `0.0.0.0`
   - `PORT`: `8000`
   - `DEBUG`: `false`
   - `CORS_ORIGINS`: `["https://your-frontend-url.vercel.app"]`

4. **Handle Data Files**
   - Render has a 100MB disk limit on free tier
   - Options:
     - Compress CSV files
     - Use Render Disk (paid tier)
     - Host data files on S3 and load from URL
     - Use a database instead of CSV files

### Option 2: Self-Hosted (VPS)

**Pros**: Full control, no limits, cost-effective at scale
**Cons**: Requires DevOps knowledge, manual maintenance

#### Server Setup (Ubuntu)

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx
   ```

2. **Clone repository**
   ```bash
   git clone <your-repo-url>
   cd jeevs-cbb
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Edit .env with production values
   ```

4. **Install and configure Systemd service for backend**
   ```bash
   sudo nano /etc/systemd/system/jeevs-cbb-api.service
   ```
   
   Content:
   ```ini
   [Unit]
   Description=Jeevs CBB API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/jeevs-cbb/backend
   Environment="PATH=/path/to/jeevs-cbb/backend/venv/bin"
   ExecStart=/path/to/jeevs-cbb/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable jeevs-cbb-api
   sudo systemctl start jeevs-cbb-api
   ```

5. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

6. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/jeevs-cbb
   ```
   
   Content:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       # Frontend
       location / {
           root /path/to/jeevs-cbb/frontend/.next;
           try_files $uri $uri.html $uri/ /index.html;
       }

       # Backend API
       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/jeevs-cbb /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

7. **SSL with Let's Encrypt**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

### Option 3: Docker Deployment

**Pros**: Consistent environment, easy scaling
**Cons**: Requires Docker knowledge

1. **Create `Dockerfile` for backend**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .
   COPY data/ ./data/

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Create `Dockerfile` for frontend**
   ```dockerfile
   FROM node:18-alpine

   WORKDIR /app
   COPY package*.json ./
   RUN npm install

   COPY . .
   RUN npm run build

   EXPOSE 3000
   CMD ["npm", "start"]
   ```

3. **Create `docker-compose.yml`**
   ```yaml
   version: '3.8'
   services:
     backend:
       build: ./backend
       ports:
         - "8000:8000"
       environment:
         - HOST=0.0.0.0
         - PORT=8000
       volumes:
         - ./backend/data:/app/data

     frontend:
       build: ./frontend
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=http://localhost:8000
       depends_on:
         - backend
   ```

4. **Deploy with Docker**
   ```bash
   docker-compose up -d
   ```

## Environment Variables

### Frontend (.env)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NODE_ENV=production
```

### Backend (.env)
```bash
HOST=0.0.0.0
PORT=8000
DEBUG=false
API_TITLE=Jeevs CBB API
API_DESCRIPTION=College Basketball Analytics API
API_VERSION=1.0.0
CORS_ORIGINS=["https://your-frontend-url.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
DATA_DIR=./data
DEFAULT_LIMIT=50
MAX_LIMIT=100
MAX_SEARCH_LENGTH=100
LOG_LEVEL=INFO
```

## Data File Considerations

The application uses CSV files for data storage. For production:

1. **File Size**: Monitor CSV file sizes
   - Large files may cause memory issues
   - Consider pagination or lazy loading

2. **Storage Options**:
   - **Local files**: Simple but limited by disk space
   - **S3/Cloud Storage**: Scalable, requires code changes
   - **Database**: Best for production, requires migration

3. **Migration to Database (Recommended for Scale)**
   - Consider PostgreSQL or MySQL
   - Use SQLAlchemy for ORM
   - Migrate CSV data to database tables

## Performance Optimization

### Frontend
- Enable Next.js Image Optimization
- Implement caching strategies
- Use CDN for static assets

### Backend
- Implement response caching
- Use connection pooling for database
- Consider Redis for caching
- Implement rate limiting

## Monitoring

1. **Logging**: Set up centralized logging (e.g., Logtail, Datadog)
2. **Error Tracking**: Use Sentry for error monitoring
3. **Uptime Monitoring**: Use UptimeRobot or Pingdom
4. **Performance**: Use Google Lighthouse or WebPageTest

## Security

1. **HTTPS**: Always use SSL certificates
2. **Environment Variables**: Never commit secrets
3. **CORS**: Restrict to your frontend domain
4. **Rate Limiting**: Implement on API endpoints
5. **Input Validation**: Validate all user inputs
6. **Dependencies**: Keep packages updated

## CI/CD

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          # Add render deploy command
          
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Checklist

- [ ] Choose deployment platform
- [ ] Set up environment variables
- [ ] Configure CORS settings
- [ ] Handle data file storage
- [ ] Set up SSL/HTTPS
- [ ] Configure domain/DNS
- [ ] Set up monitoring
- [ ] Test all API endpoints
- [ ] Test frontend functionality
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
