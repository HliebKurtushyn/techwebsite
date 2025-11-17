import jwt
from fastapi import Cookie, Depends, HTTPException, Response

from app.core.config import SECRET_KEY, ALGORITHM
from app.models.user import User

__all__ = ["get_current_user", "clear_flash_cookie"]

def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or role is None:
            return None
        return username, user_id, role
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def admin_required(user: User = Depends(get_current_user)):
    if user is None or user[2] != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")
    return user


async def login_required(user: User = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user


def clear_flash_cookie(response: Response):
    response.delete_cookie("flash_msg")