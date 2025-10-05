import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.infrastructure.db.base import Base, engine
from app.interfaces.http.api_router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(settings.log_level)
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="SEO Compass",
    description="Automated SEO Analysis & Content Generation Platform - Transform any URL into comprehensive SEO insights with competitor analysis, keyword research, and AI-generated content drafts.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "SEO Compass API",
        "url": "https://github.com/your-repo/seo-compass",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID middleware."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": "seo-compass",
        "version": "0.1.0"
    }


# Include API routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )