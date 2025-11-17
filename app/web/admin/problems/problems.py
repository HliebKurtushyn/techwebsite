from fastapi import Depends, Form, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_session
from app.core.dependencies import admin_required, get_current_user
from app.models.problem import Problem
from app.models.user import User


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/problem_list')
async def problem_list(request: Request,session: AsyncSession = Depends(get_session) , is_admin: int = Depends(admin_required)):
    problem_list = await session.execute(select(Problem.id, Problem.title, Problem.description, Problem.date_created).filter_by(status="В обробці"))
    problem_list = problem_list.all()

    print(problem_list)

    return templates.TemplateResponse('admin/problems/problem_list.html',{'request': request, 'problem_list': problem_list})


@router.get('/problem')
async def problem(request_id: int, request: Request, session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    problem = await session.execute(select(Problem).filter_by(id = request_id))
    problem = problem.scalars().first()
    return templates.TemplateResponse('admin/problems/problem.html', {'request': request, 'problem': problem})


@router.post('/problem')
async def problem(request: Request, current_user: User = Depends(get_current_user),id:int=Form(), session: AsyncSession = Depends(get_session), is_admin: int = Depends(admin_required)):
    problem = await session.execute(select(Problem).filter_by(id=id))
    problem = problem.scalar_one_or_none()
    if problem:
        problem.status = 'У роботі'
        problem.admin_id = current_user[0]
        session.add(problem)
        await session.commit()
        await session.refresh(problem)
    return templates.TemplateResponse('admin/problems/problem.html', {'request': request, 'problem': problem, 'flash_msg':'Заявку взято в роботу!'})
