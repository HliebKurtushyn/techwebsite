import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Response, Depends
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.dependencies import *
from app.api.v1.__init__ import SECRET_KEY


load_dotenv()

ALGORITHM = "HS256"

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
async def home(request: Request, user: tuple | None = Depends(get_current_user, use_cache=False)):
    flash_msg = request.cookies.get("flash_msg")
    
    template_response = templates.TemplateResponse(
        "home/home.html",
        {"request": request, "flash_msg": flash_msg, "user": user}
    )
    if flash_msg:
        template_response.delete_cookie("flash_msg")
    
    return template_response
