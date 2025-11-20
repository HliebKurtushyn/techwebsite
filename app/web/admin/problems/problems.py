from fastapi import Depends, Form, APIRouter, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.core.dependencies import admin_required, get_current_user
from app.models.admin_response import AdminResponse
from app.models.problem import Problem
from app.models.user import User
from app.models.service_record import ServiceRecord
from datetime import date, timedelta


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get('/list')
async def admin_problem_list(request: Request, session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    result = await session.execute(
        select(Problem)
        .options(selectinload(Problem.user), selectinload(Problem.admin))
        .filter_by(status="В обробці")
    )
    problem_list = result.scalars().all()

    return templates.TemplateResponse('admin/problems/problem_list.html', {'request': request, 'problem_list': problem_list})


@router.get('/problem')
async def admin_problem(request: Request, problem_id: int, session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    result = await session.execute(
    select(Problem)
    .options(selectinload(Problem.user), selectinload(Problem.admin))
    .filter_by(id=problem_id)
    )

    problem = result.scalars().first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return templates.TemplateResponse('admin/problems/problem.html', {'request': request, 'problem': problem})


@router.post('/problem')
async def admin_problem_post(
    request: Request,
    problem_id: int = Form(...),
    current_user: tuple | None = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    is_admin: int = Depends(admin_required),
):

    result = await session.execute(
        select(Problem).options(selectinload(Problem.user), selectinload(Problem.admin)).filter_by(id=problem_id)
    )
    problem = result.scalars().one_or_none()
    if problem:
        problem.status = 'У роботі'
        if not current_user or len(current_user) < 2:
            raise HTTPException(status_code=401, detail="Authentication required to assign admin")
        problem.admin_id = current_user[1]
        session.add(problem)
        await session.commit()
        await session.refresh(problem)

    return templates.TemplateResponse(
        'admin/problems/problem.html',
        {'request': request, 'problem': problem, 'flash_msg': 'The request has been taken into work!'},
    )


@router.get('/admin_problems')
async def admin_problems(request: Request, current_user: tuple | None = Depends(get_current_user), session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    admin_id = current_user[1]
    new_problems = await session.execute(select(Problem).filter_by(admin_id=admin_id))
    new_problems = new_problems.scalars().all()
    return templates.TemplateResponse('admin/problems/admin_problems.html', {'request': request, 'problems': new_problems})


@router.get('/add_answer')
async def add_answer( problem_id: int,request: Request, is_admin: int = Depends(admin_required)):
    return templates.TemplateResponse('admin/problems/add_answer.html', {'request': request, 'id':problem_id})

@router.post('/add_answer')
async def add_answer_post(request: Request, problem_id: int = Form(), current_user: tuple | None = Depends(get_current_user), message: str = Form(), session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    new_answer = AdminResponse(message=message, admin_id=current_user[1], problem_id=problem_id)
    session.add(new_answer)
    await session.commit()

    result = await session.execute(select(Problem).filter_by(id=problem_id))
    problem = result.scalars().one_or_none()
    if problem:
        problem.status = 'Є відповідь'
        session.add(problem)
        await session.commit()
    return templates.TemplateResponse('admin/problems/add_answer.html', {'request': request, 'flash_msg': 'Answer saved!'})

# ТИМЧАСОВО НЕ ПРАЦЮЄ
@router.get('/service_complete')
async def service_complete_get(problem_id:int, request: Request):
    return templates.TemplateResponse('admin/problems/service_complete.html',{'request':request, "problem_id":problem_id})

# ТАКОЖ НЕ ПРАЦЮЄ
@router.post('/service_complete')
async def service_complete(request: Request, work_done: str = Form(), parts_used: str = Form(), problem_id:int = Form(),current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    problem = await session.execute(select(Problem).filter_by(id=problem_id))
    problem = problem.scalars().one_or_none()
    warranty_info = f"# {problem_id}\\nТип послуги: сервісне обслуговування\\nДата початку робіт: {problem.date_created.date()}\\nДата завершення робіт: {date.today()}\\nГарантія розповсюджується на деталі що використовувалися в роботі, та механізми що були полагоджені\\nДата завершення гарантії: {date.today() + timedelta(days=180)}"
    new_service_record = ServiceRecord(work_done=work_done, parts_used=parts_used, problem_id=problem_id,warranty_info=warranty_info)
    session.add(new_service_record)
    await session.commit()
    problem.status = 'Завершено'
    session.add(problem)
    await session.commit()
    return templates.TemplateResponse('admin/problems/service_complete.html', {'request': request, "message": 'Запис додано!'})