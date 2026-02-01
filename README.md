# FastAPI Backend

Clean architecture FastAPI project with MongoDB.

## Features
- **FastAPI** (High performance, easy to learn, fast to code, ready for production)
- **MongoDB** (Motor async driver)
- **Authentication** (JWT with HTTPBearer security scheme)
- **Environment Separation** (Dev/Prod configurations)
- **Testing** (Pytest coverage for Auth and Bookings)
- **Docker & Docker Compose**

## Setup

### 1. Environment Variables
The system now uses separated environment files.
- `.env.dev`: Development configuration
- `.env.prod`: Production configuration

**Auto-setup for Docker:**
A local `.env` file (copy of `.env.dev`) is required for `docker-compose` to start without arguments.
```bash
cp .env.example .env.dev
cp .env.dev .env  # Required for default docker-compose up
```

### 2. Docker
Run the application container:
```bash
docker-compose up -d --build
```
The API will be available at `http://localhost:8000`.

### 3. Local Development (No Docker)
If you wish to run locally:
```bash
# Set environment
export ENVIRONMENT=dev  # Uses .env.dev

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Authentication & Swagger UI
1. Go to `http://localhost:8000/docs`.
2. Use the `/api/auth/register` endpoint to create a user.
3. Use the `/api/auth/login` endpoint to get an `access_token`.
4. Click the **Authorize** button at the top of the page.
5. Paste your `access_token` into the box (value: `your_token_string`).
6. You can now access protected endpoints like `GET /api/bookings`.

## Testing
Unit tests are included for Authentication and Booking flows.
**Run tests inside Docker (recommended):**
```bash
docker-compose exec backend pytest -v tests/
```

**Run local tests:**
```bash
export ENVIRONMENT=dev
pytest -v tests/
```

## SonarQube & CI/CD
A `sonar-project.properties` file is included for code quality analysis.
To run this in a CI/CD pipeline, ensure the following environment variables are set:
- `SONAR_HOST_URL`: URL of your SonarQube server (e.g., `http://localhost:9000`)
- `SONAR_TOKEN`: Authentication token from SonarQube (My Account > Security > Generate Tokens)

**Local Analysis:**
1. Start SonarQube: `docker-compose up -d sonarqube`
2. Access at `http://localhost:9000` (Default: admin/admin)
3. Run tests with coverage: `pytest --cov=app --cov-report=xml tests/`
4. Run scanner (requires sonar-scanner CLI installed locally).

## Project Structure
- `app/core`: Configuration, Database, Security, Dependency Injection
- `app/models`: Database models
- `app/schemas`: Pydantic data schemas
- `app/routes`: API route handlers
- `app/repositories`: Database access layer
- `tests/`: Unit and integration tests
