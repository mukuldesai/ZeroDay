# ZeroDay Deployment Guide

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Local Development Setup

```bash
git clone https://github.com/mukuldesai/ZeroDay.git
cd zeroday

python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

cd frontend
npm install
cd ..

cp .env.example .env
```

### Environment Variables

Create `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=sqlite:///database/users.db
DEMO_MODE=true
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Initialize Database

```bash
python database/setup.py
python -m scripts.setup_demo
```

### Start Development Servers

Backend:
```bash
python api/main.py
```

Frontend (new terminal):
```bash
cd frontend
npm run dev
```

Access application at `http://localhost:3000`

## Production Deployment

### Option 1: Vercel + Railway

**Frontend (Vercel):**
1. Connect GitHub repository to Vercel
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/.next`
4. Add environment variables in Vercel dashboard

**Backend (Railway):**
1. Connect repository to Railway
2. Set start command: `python api/main.py`
3. Add environment variables
4. Configure custom domain

### Option 2: Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api/main.py"]
```

```bash
docker build -t zeroday .
docker run -p 8000:8000 --env-file .env zeroday
```

### Option 3: VPS Deployment

```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx

git clone https://github.com/yourusername/zeroday.git
cd zeroday

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..

sudo systemctl enable nginx
sudo systemctl start nginx
```

**Nginx Configuration (`/etc/nginx/sites-available/zeroday`):**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Setup

### SQLite (Development)
```bash
python database/setup.py
```

### PostgreSQL (Production)
```bash
pip install psycopg2-binary
export DATABASE_URL=postgresql://user:password@localhost/zeroday
python database/setup.py
```

## Vector Store Setup

### ChromaDB (Default)
```bash
python vector_store/chromadb_setup.py init
python vector_store/demo_vectorstore.py populate_all
```

### Production Vector Store
```bash
export CHROMA_SERVER_HOST=your-chroma-host
export CHROMA_SERVER_PORT=8000
python vector_store/chromadb_setup.py init
```

## Demo Data Setup

```bash
python scripts/setup_demo.py
python vector_store/demo_vectorstore.py populate_all
```

## Health Checks

Backend health: `GET /api/health`
Vector store health: `python vector_store/chromadb_setup.py health`
Database health: `python database/setup.py check`

## Scaling Configuration

### Environment-Specific Settings

**Development:**
```env
DEBUG=true
DEMO_MODE=true
LOG_LEVEL=DEBUG
```

**Production:**
```env
DEBUG=false
DEMO_MODE=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Performance Tuning

**Backend:**
- Use gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app`
- Enable caching with Redis
- Configure database connection pooling

**Frontend:**
- Enable production build: `npm run build`
- Configure CDN for static assets
- Enable compression in Next.js config

## Monitoring

### Application Logs
```bash
tail -f logs/app.log
tail -f logs/vector_store.log
```

### Performance Monitoring
- Database query performance
- Vector search latency
- API response times
- Memory usage

## Backup Strategy

### Database Backup
```bash
python scripts/backup_database.py
```

### Vector Store Backup
```bash
python vector_store/chromadb_setup.py backup
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Database connection issues:**
```bash
python database/setup.py check
```

**Vector store issues:**
```bash
python vector_store/chromadb_setup.py health
```

**Demo data missing:**
```bash
python scripts/reset_database.py
python scripts/setup_demo.py
```

### Debug Mode

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python api/main.py
```

## Security Checklist

- [ ] Environment variables configured
- [ ] Secret keys generated
- [ ] CORS origins restricted
- [ ] HTTPS enabled in production
- [ ] Database credentials secured
- [ ] API rate limiting enabled
- [ ] Input validation implemented
- [ ] Authentication middleware active

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Validate vector store setup
5. Check network configuration

Repository: https://github.com/mukuldesai/ZeroDay
Documentation: /docs
Demo: https://your-demo-url.com