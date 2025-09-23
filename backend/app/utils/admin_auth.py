import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Request

SECRET_KEY = os.getenv("ADMIN_JWT_SECRET", "CHANGE_ME_ADMIN_SECRET")
ALGORITHM = "HS256"
EXPIRES_MIN = int(os.getenv("ADMIN_JWT_EXPIRES_MIN", "60"))

def create_admin_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRES_MIN),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def require_admin_token(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token sem privilégios de admin")
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
