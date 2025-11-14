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
from starlette.exceptions import HTTPException as StarletteHTTPException

import bcrypt
import jwt

from app.api.v1_endpoints import api_v1_router
from app.db.session import Base, async_session, engine
from app.models.__init__ import *
from app.core.handlers.exceptions import not_found_handler, access_denied_handler

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

app.add_exception_handler(StarletteHTTPException, not_found_handler)
app.add_exception_handler(StarletteHTTPException, access_denied_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_v1_router)

templates = Jinja2Templates(directory="app/templates")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    await init_db()
