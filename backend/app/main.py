"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.middleware.auth_context import AuthContextMiddleware
from app.core.config import settings
from app.core.database import engine
from app.db.base import Base
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting up DineBuddy backend...")
    print(f"📊 Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    
    # Note: We use Alembic migrations for database schema management
    # Tables are created by running: alembic upgrade head
    # (handled automatically in docker-compose.yml startup command)
    
    yield
    
    # Shutdown
    print("👋 Shutting down DineBuddy backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Restaurant Management System API",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthContextMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DineBuddy API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }
