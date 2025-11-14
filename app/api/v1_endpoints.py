from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.home import router as home_router
from app.api.v1.requests import router as requests_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(auth_router, prefix="/auth")
api_v1_router.include_router(home_router)
api_v1_router.include_router(requests_router, prefix="/requests")