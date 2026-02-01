from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.logging import setup_logging
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Wednesday's Wicked Adventures",
    description="""
## Horror-themed Adventure Park Booking System

Book your thrilling experience at our adventure parks:
- 🎢 **Risky Rollercoaster** - Our most popular attraction!
- 👻 **Haunted Mansion** - For the brave souls
- 🌲 **Nightfall Woods** - Adventure in the dark

### Features
- Customer booking portal
- Admin management (Wednesday & Pugsley)
- Health and safety consent tracking
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan
)

# Custom OpenAPI schema to include security schemes
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"message": "Welcome to Wednesday's Wicked Adventures API", "status": "healthy"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "Wednesday's Wicked Adventures API",
        "version": "1.0.0"
    }
