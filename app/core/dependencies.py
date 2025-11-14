import jwt
from fastapi import Cookie, HTTPException, Response
from app.core.config import SECRET_KEY, ALGORITHM

__all__ = ["get_current_user", "clear_flash_cookie"]

def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or role is None:
            return None
        return user_id, role
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def clear_flash_cookie(response: Response):
    response.delete_cookie("flash_msg")