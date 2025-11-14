from fastapi import APIRouter
from app.web.auth.auth import router as auth_router
from app.web.home.home import router as home_router
from app.web.requests.requests import router as requests_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(home_router)
router.include_router(requests_router, prefix="/requests")