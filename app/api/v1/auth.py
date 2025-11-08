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

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
async def home(request: Request):
    return {"message": "Вітаємо на нашому сайті!)"}


@router.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    new_user = User(username=username, email=email)
    new_user.set_password(raw_password=password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "message": "Ви успішно створили акаунт!"},
    )


def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Неавторизовано")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(status_code=401)
        return user_id, role
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Недійсний токен")


@router.get("/login")
async def login_get(request: Request, error: str = None):
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error}
    )


@router.post("/login")
async def login_post(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()

    if not user or not bcrypt.checkpw(form_data.password.encode(), user.password.encode()):
        return RedirectResponse(
            url="/login/?error=Пароль або логін невірний, спробуйте ще раз",
            status_code=302,
        )

    token_data = {
        "user_id": user.id,
        "role": "admin" if user.is_admin else "user",
        "exp": datetime.utcnow() + timedelta(days=3),
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 3,
        samesite="lax",
    )
    return response


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Ви вийшли з системи"}
