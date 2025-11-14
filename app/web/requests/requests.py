from fastapi import APIRouter, Request, Response, Depends, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import clear_flash_cookie, get_current_user
from app.db.session import get_session
from app.models.problem import Problem
from app.models.user import User


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

UPLOAD_DIR = "static/requests_images"


@router.get('/new')
async def service_request(request: Request):
    flash_msg = request.cookies.get("flash_msg")
    template_response =  templates.TemplateResponse('requests/service_request.html', {'request': request, 'flash_msg': flash_msg})

    if flash_msg:
        clear_flash_cookie(template_response)

    return template_response

@router.post('/new')
async def service_request_post(request: Request, title:str=Form(), description:str=Form(), img = File(None), current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    img_path = None
    if img.filename:
        file_location = f"requests_images/{img.filename}"
        with open('static/'+ file_location, "wb+") as f:
            f.write(await img.read())
        img_path = file_location

    new_problem = Problem(
        title=title,
        description=description,
        user_id=current_user[0],
        image_url=img_path
    )

    session.add(new_problem)
    await session.commit()
    await session.refresh(new_problem)

    redirect = RedirectResponse(url="/", status_code=302)
    redirect.set_cookie(key="flash_msg", value="Successfully created a service request!")

    return redirect
