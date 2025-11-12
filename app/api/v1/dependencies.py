from dotenv import load_dotenv
from fastapi import Cookie, HTTPException
import jwt
import os

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")


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
    