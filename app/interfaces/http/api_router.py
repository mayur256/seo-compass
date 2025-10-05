from fastapi import APIRouter
from .v1.analysis import router as analysis_router

api_router = APIRouter()
api_router.include_router(analysis_router, prefix="/v1", tags=["analysis"])