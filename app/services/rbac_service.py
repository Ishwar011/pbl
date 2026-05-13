from fastapi import Depends, HTTPException
from jose import jwt
from fastapi.security import HTTPBearer
from app.services.auth_service import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_user(token=Depends(security)):

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
