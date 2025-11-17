import os

from pathlib import Path
from fastapi import APIRouter, Request, Response, Depends, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import clear_flash_cookie, get_current_user
from app.db.session import get_session
from app.models.problem import Problem
from app.models.user import User


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "problems_images"


@router.get('/')
async def problems(
    request: Request, 
    user: tuple | None = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    flash_msg = request.cookies.get("flash_msg")

    stmt = (
        select(Problem)
        # Завантажуємо пов'язаний об'єкт 'user'
        .options(selectinload(Problem.user)) 
        # Завантажуємо пов'язаний об'єкт 'admin'
        .options(selectinload(Problem.admin))
    )

    result = await session.execute(stmt)
    problems = result.scalars().all()

    template_response = templates.TemplateResponse(
            'problems/problems.html', 
            {'request': request, 'flash_msg': flash_msg, 'user': user, 'problems': problems}
        )
    
    if flash_msg:
        clear_flash_cookie(template_response)

    return template_response


@router.get('/new')
async def problem_request(request: Request):
    flash_msg = request.cookies.get("flash_msg")
    template_response =  templates.TemplateResponse('problems/problem_request.html', {'request': request, 'flash_msg': flash_msg})

    if flash_msg:
        clear_flash_cookie(template_response)

    return template_response

@router.post('/new')
async def problem_request_post(
    response: Response,
    title: str = Form(), 
    description: str = Form(), 
    img = File(None), 
    current_user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    img_path = None
    
    if img and img.filename:
        file_location = UPLOAD_DIR / img.filename
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(file_location, "wb+") as f:
            f.write(await img.read())  
        img_path = f"problems_images/{img.filename}"

    new_problem = Problem(
        title=title,
        description=description,
        user_id=current_user[1],
        image_url=img_path
    )

    session.add(new_problem)
    await session.commit()
    await session.refresh(new_problem)

    redirect_url = router.url_path_for('problem_request')
    redirect = RedirectResponse(url=redirect_url, status_code=302)
    redirect.set_cookie(key="flash_msg", value="Successfully created a problem request!")

    return redirect
