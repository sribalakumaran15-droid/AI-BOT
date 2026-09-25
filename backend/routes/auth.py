from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import User
from backend.utils.auth import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
class RegisterBody(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    college: str = ""
    department: str = ""
class LoginBody(BaseModel):
    email: EmailStr
    password: str

def user_payload(user):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "college": user.college, "department": user.department}

@router.post("/register", status_code=201)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if body.password != body.confirm_password:
        raise HTTPException(400, "Passwords do not match.")
    if db.query(User).filter(User.email == body.email.lower()).first():
        raise HTTPException(409, "An account with this email already exists.")
    user = User(full_name=body.full_name.strip(), email=body.email.lower(), password_hash=hash_password(body.password), college=body.college.strip(), department=body.department.strip())
    db.add(user); db.commit(); db.refresh(user)
    return {"success": True, "token": create_token(user.id), "user": user_payload(user)}

@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return {"success": True, "token": create_token(user.id), "user": user_payload(user)}
