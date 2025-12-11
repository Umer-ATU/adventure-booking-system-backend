# FastAPI Backend

Clean architecture FastAPI project with MongoDB.

## Features
- FastAPI
- MongoDB (Motor)
- Docker & Docker Compose
- JWT Authentication ready
- Pre-commit hooks (Black, Isort, Flake8)

## Setup

1. **Environment Variables**
   ```bash
   cp .env.example .env
   ```

2. **Docker**
   ```bash
   docker-compose up -d --build
   ```

3. **Local Development**
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## Structure
- `app/core`: Configuration, Database, Settings
- `app/models`: Database models
- `app/schemas`: Pydantic schemas
- `app/routes`: API endpoints
- `app/services`: Business logic
