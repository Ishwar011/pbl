from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database import models
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(username: str, password: str, role: str, db: Session = Depends(get_db)):

    user = models.User(
        username=username,
        password_hash=hash_password(password),
        role=role
    )

    db.add(user)
    db.commit()
    return {"message": "User created"}

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == request.username).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})

    return {"access_token": token, "role": user.role}