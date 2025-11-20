import os

from pathlib import Path
from fastapi import APIRouter, Request, Response, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import clear_flash_cookie, get_current_user, login_required
from app.db.session import get_session
from app.models.problem import Problem
from app.models.user import User
from app.models.admin_response import AdminResponse
from app.models.service_record import ServiceRecord

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "problems_images"


@router.get('/')
async def problems(
    request: Request, 
    user: tuple | None = Depends(login_required),
    session: AsyncSession = Depends(get_session)
):
    flash_msg = request.cookies.get("flash_msg")

    stmt = (
        select(Problem)
        .filter_by(user_id=user[1])
        .options(selectinload(Problem.user)) 
        .options(selectinload(Problem.admin))
    )

    result = await session.execute(stmt)
    problems = result.scalars()

    template_response = templates.TemplateResponse(
            'problems/problems.html', 
            {'request': request, 'flash_msg': flash_msg, 'user': user, 'problems': problems}
        )
    
    if flash_msg:
        clear_flash_cookie(template_response)

    return template_response


@router.get('/new')
async def problem_request(request: Request, user: tuple | None = Depends(login_required)):
    flash_msg = request.cookies.get("flash_msg")
    template_response =  templates.TemplateResponse('problems/problem_request.html', {'request': request, 'flash_msg': flash_msg})

    if flash_msg:
        clear_flash_cookie(template_response)

    return template_response

@router.post('/new')
async def problem_request_post(
    response: Response,
    user: tuple | None = Depends(login_required),
    title: str = Form(),
    description: str = Form(),
    img = File(None),
    current_user: tuple | None = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    img_path = None
    
    if img and img.filename:
        file_location = UPLOAD_DIR / img.filename
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(file_location, "wb+") as f:
            f.write(await img.read())  
        img_path = f"problems_images/{img.filename}"

    if not current_user or len(current_user) < 2:
        raise HTTPException(status_code=401, detail="Authentication required")

    new_problem = Problem(
        title=title,
        description=description,
        user_id=current_user[1],
        image_url=img_path,
    )

    session.add(new_problem)
    await session.commit()
    await session.refresh(new_problem)

    redirect_url = router.url_path_for('problem_request')
    redirect = RedirectResponse(url=redirect_url, status_code=302)
    redirect.set_cookie(key="flash_msg", value="Successfully created a problem request!")

    return redirect


@router.get('/my_all_problems')
async def my_all_problems(request: Request, current_user: tuple | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_id = current_user[1]
    all_problems = await session.execute(select(Problem).filter_by(user_id=user_id))
    problems = all_problems.scalars().all()
    return templates.TemplateResponse('problems/all_my_problems.html', {'request': request, 'problems': problems})


@router.get('/view', name='view_problem')
async def view_problem(request: Request, problem_id: int, session: AsyncSession = Depends(get_session)):
    # View a single problem (user-facing)
    result = await session.execute(
        select(Problem).options(selectinload(Problem.user), selectinload(Problem.admin)).filter_by(id=problem_id)
    )
    problem = result.scalars().one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return templates.TemplateResponse('problems/problem_detail.html', {'request': request, 'problem': problem})


@router.get('/check_message')
async def check_message(id: int, request: Request, current_user: tuple | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Problem).filter_by(id=id))
    problem = result.scalars().one_or_none()
    result2 = await session.execute(select(AdminResponse).filter_by(problem_id=id))
    problem_answer = result2.scalars().one_or_none()
    return templates.TemplateResponse('problems/check_message.html', {'request': request, 'problem': problem, 'answer': problem_answer})


@router.get('/service_record_review')
async def service_record_review(id:int, request: Request, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    problem = await session.execute(select(Problem).filter_by(id=id))
    problem = problem.scalars().one_or_none()
    service_record = await session.execute(select(ServiceRecord).filter_by(problem_id = id))
    my_service_record = service_record.scalars().one_or_none()
    return templates.TemplateResponse('problems/service_check.html',{'request':request, 'problem':problem, 'service_record':my_service_record})