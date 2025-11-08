import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import (FastAPI, Depends, Form, HTTPException, Request, status)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import bcrypt
import jwt

from app.api.v1.auth import router as auth_router
from app.db.session import Base, async_session, engine
from app.models.problem import Problem
from app.models.user import User
from app.models.service_record import ServiceRecord
from app.models.admin_response import AdminResponse


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth_router)


templates = Jinja2Templates(directory="app/templates")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    await init_db()
