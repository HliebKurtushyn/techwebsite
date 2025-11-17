from fastapi import APIRouter
from app.web.auth.auth import router as auth_router
from app.web.home.home import router as home_router
from app.web.problems.problems import router as problems_router
from app.web.admin.problems.problems import router as admin_problems_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(home_router)
router.include_router(problems_router, prefix="/problems")
router.include_router(admin_problems_router, prefix="/admin/problems")