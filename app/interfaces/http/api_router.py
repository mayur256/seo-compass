from fastapi import APIRouter
from .v1.analysis import router as analysis_router
from .v1.reports import router as reports_router

api_router = APIRouter()

api_router.include_router(
    analysis_router, 
    prefix="/v1", 
    tags=["SEO Analysis"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

api_router.include_router(
    reports_router,
    prefix="/v1/reports",
    tags=["Reports"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)