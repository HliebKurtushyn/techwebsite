import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Form, Depends, Response, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import bcrypt
import jwt

from app.db.session import get_session
from app.models.user import User
from app.core.config import ALGORITHM, SECRET_KEY
from app.core.dependencies import *


load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/signup")
async def signup(request: Request):
    flash_msg = request.cookies.get("flash_msg")
    response = templates.TemplateResponse(
        "auth/signup.html",
        {"request": request, "flash_msg": flash_msg},
    )
    clear_flash_cookie(response)
    return response


@router.post("/signup")
async def signup_post(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).filter(User.username == username))
    if result.scalars().first():
        redirect = RedirectResponse(url="/auth/signup", status_code=302)
        redirect.set_cookie(key="flash_msg", value="Username already exists.")
        return redirect

    new_user = User(username=username, email=email)
    new_user.set_password(raw_password=password)
    session.add(new_user)
    await session.commit()

    redirect = RedirectResponse(url="/auth/login", status_code=302)
    redirect.set_cookie(key="flash_msg", value="Successfully created an account!")
    return redirect


@router.get("/login")
async def login(request: Request):
    flash_msg = request.cookies.get("flash_msg")
    response = templates.TemplateResponse(
        "auth/login.html", {"request": request, "flash_msg": flash_msg}
    )
    clear_flash_cookie(response)
    return response


@router.post("/login")
async def login_post(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()

    if not user or not bcrypt.checkpw(form_data.password.encode(), user.password.encode()):
        redirect = RedirectResponse(url="/auth/login", status_code=302)
        redirect.set_cookie(key="flash_msg", value="Incorrect username or password.")
        return redirect

    token_data = {
        "username": user.username,
        "user_id": user.id,
        "role": "admin" if user.is_admin else "user",
        "exp": datetime.utcnow() + timedelta(days=3),
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    redirect = RedirectResponse(url="/", status_code=302)
    redirect.set_cookie(key="flash_msg", value="Successfully logged in")
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 3,
        samesite="lax",
    )
    return redirect


@router.post("/logout")
async def logout():
    redirect = RedirectResponse(url="/", status_code=302)
    redirect.set_cookie(key="flash_msg", value="Successfully logged out")
    redirect.delete_cookie("access_token")
    return redirect