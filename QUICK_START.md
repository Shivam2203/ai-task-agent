# Quick Start Guide - AI Task Completion Agent

This guide will help you get the AI Task Completion Agent up and running in under 30 minutes.

## Prerequisites Checklist

- [ ] Python 3.11 or higher installed
- [ ] Node.js 20 or higher installed
- [ ] PostgreSQL 16+ installed
- [ ] Docker and Docker Compose installed (recommended)
- [ ] IBM watsonx.ai account with API credentials
- [ ] Git installed

## Option 1: Docker Setup (Recommended)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-task-agent

# Create environment file
cp backend/.env.example backend/.env
```

### Step 2: Configure Environment Variables

Edit `backend/.env` with your credentials:

```env
# watsonx.ai Credentials (REQUIRED)
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Database (auto-configured by Docker)
DATABASE_URL=postgresql+asyncpg://taskagent:taskagent_password@postgres:5432/taskagent_db

# Redis (auto-configured by Docker)
REDIS_URL=redis://redis:6379

# Application
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Step 3: Start Services

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 5: Verify Installation

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status": "healthy", "database": "connected", "redis": "connected"}
```

## Option 2: Manual Setup

### Step 1: Database Setup

```bash
# Install PostgreSQL with pgvector
# On Ubuntu/Debian:
sudo apt-get install postgresql-16 postgresql-16-pgvector

# On macOS with Homebrew:
brew install postgresql@16
brew install pgvector

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql@16  # macOS

# Create database
createdb taskagent_db

# Enable pgvector extension
psql taskagent_db -c "CREATE EXTENSION vector;"
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 4: Redis Setup (Optional but Recommended)

```bash
# Install Redis
# On Ubuntu/Debian:
sudo apt-get install redis-server

# On macOS:
brew install redis

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis  # macOS
```

## First Task Example

### Using the Web Interface

1. Open http://localhost:3000
2. Enter a task title: "Create a Python function"
3. Enter description: "Create a Python function that calculates the Fibonacci sequence up to n terms"
4. Click "Start Task"
5. Watch the agent plan, execute, and verify the task in real-time

### Using the API

```bash
# Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Create a Python function",
    "description": "Create a Python function that calculates the Fibonacci sequence up to n terms"
  }'

# Response will include task_id
# {"id": "uuid-here", "title": "...", "status": "pending", ...}

# Get task status
curl http://localhost:8000/api/v1/tasks/{task_id}
```

## Project Structure Overview

```
ai-task-agent/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Agent, LLM, RAG
│   │   ├── models/      # Data models
│   │   └── db/          # Database
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # UI components
│       ├── hooks/       # Custom hooks
│       └── services/    # API services
├── docker/              # Docker configuration
└── docs/                # Documentation
```

## Common Commands

### Backend

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Format code
black app/
isort app/

# Type checking
mypy app/

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend

```bash
# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild services
docker-compose build

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

## Configuration Guide

### watsonx.ai Setup

1. **Get API Key**:
   - Log in to IBM Cloud
   - Navigate to watsonx.ai
   - Go to API Keys section
   - Create new API key

2. **Get Project ID**:
   - Create or select a project in watsonx.ai
   - Copy the Project ID from project settings

3. **Configure URL**:
   - Use region-specific URL:
     - US South: `https://us-south.ml.cloud.ibm.com`
     - EU: `https://eu-de.ml.cloud.ibm.com`
     - Tokyo: `https://jp-tok.ml.cloud.ibm.com`

### Database Configuration

```env
# Local PostgreSQL
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/taskagent_db

# Docker PostgreSQL
DATABASE_URL=postgresql+asyncpg://taskagent:taskagent_password@postgres:5432/taskagent_db
```

### Redis Configuration

```env
# Local Redis
REDIS_URL=redis://localhost:6379

# Docker Redis
REDIS_URL=redis://redis:6379

# Redis with password
REDIS_URL=redis://:password@localhost:6379
```

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Connection refused` to database
```bash
# Solution: Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check connection
psql -U postgres -h localhost
```

### Frontend won't start

**Error**: `EADDRINUSE: address already in use`
```bash
# Solution: Port 3000 is in use, kill the process or use different port
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000  # Windows (then kill PID)

# Or use different port
npm run dev -- --port 3001
```

### Docker issues

**Error**: `Cannot connect to Docker daemon`
```bash
# Solution: Start Docker
sudo systemctl start docker  # Linux
# Or start Docker Desktop on macOS/Windows
```

**Error**: `Port already allocated`
```bash
# Solution: Stop conflicting services or change ports in docker-compose.yml
docker-compose down
# Edit docker/docker-compose.yml to use different ports
docker-compose up -d
```

### Agent not responding

**Check 1**: Verify watsonx.ai credentials
```bash
# Test API connection
curl -X POST "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

**Check 2**: Check backend logs
```bash
# Docker
docker-compose logs -f backend

# Manual
# Check terminal where uvicorn is running
```

**Check 3**: Verify database connection
```bash
# Check if tables exist
psql taskagent_db -c "\dt"

# Should show: tasks, agent_states, embeddings
```

## Performance Tips

### For Development

1. **Use Docker**: Simplifies setup and ensures consistency
2. **Enable Hot Reload**: Both backend and frontend support hot reload
3. **Use Redis**: Significantly improves response times
4. **Limit Iterations**: Set `MAX_AGENT_ITERATIONS=3` for faster testing

### For Production

1. **Use Connection Pooling**: Configure SQLAlchemy pool size
2. **Enable Caching**: Use Redis for frequently accessed data
3. **Optimize Vector Search**: Tune pgvector index parameters
4. **Monitor Resources**: Set up Prometheus + Grafana

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Implementation Plan**: See `IMPLEMENTATION_PLAN.md`
3. **Review Architecture**: See `ARCHITECTURE.md`
4. **Run Tests**: Ensure everything works
5. **Customize**: Modify agent behavior, add features

## Getting Help

- **Documentation**: Check `docs/` directory
- **API Reference**: http://localhost:8000/docs
- **Issues**: Create GitHub issue
- **Logs**: Check backend and frontend logs

## Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use strong database passwords
- [ ] Enable HTTPS
- [ ] Set up proper CORS origins
- [ ] Implement rate limiting
- [ ] Enable authentication
- [ ] Review and restrict API access
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Backup database regularly

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test Changes**
   ```bash
   # Backend
   cd backend
   pytest
   
   # Frontend
   cd frontend
   npm test
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Describe changes
   - Link related issues
   - Request review

## Useful Resources

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **React Documentation**: https://react.dev/
- **LangGraph Guide**: https://langchain-ai.github.io/langgraph/
- **watsonx.ai Docs**: https://www.ibm.com/docs/en/watsonx-as-a-service
- **pgvector Guide**: https://github.com/pgvector/pgvector
- **ChromaDB Docs**: https://docs.trychroma.com/

---

**Ready to start?** Follow Option 1 (Docker) for the fastest setup, or Option 2 (Manual) for more control. Once running, try the First Task Example to see the agent in action!