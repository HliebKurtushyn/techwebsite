from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

templates = Jinja2Templates(directory="app/templates")

async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=HTTP_404_NOT_FOUND)

async def access_denied_handler(request: Request, exc):
    return templates.TemplateResponse("errors/403.html", {"request": request}, status_code=HTTP_403_FORBIDDEN)

async def unauthorized_handler(request: Request, exc):
    return templates.TemplateResponse("errors/401.html", {"request": request}, status_code=HTTP_401_UNAUTHORIZED)