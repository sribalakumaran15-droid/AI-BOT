from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import User, Course, Document, ChatMessage, QuizResult
from backend.utils.auth import current_user

router = APIRouter(prefix="/api", tags=["users"])
class ProfileBody(BaseModel):
    full_name: str
    college: str = ""
    department: str = ""

def payload(user):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "college": user.college, "department": user.department}

@router.get("/profile")
def profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"success": True, "user": payload(user), "stats": {"documents": db.query(Document).filter_by(owner_id=user.id).count(), "questions": db.query(ChatMessage).join(ChatMessage.session).filter_by(owner_id=user.id, role="user").count(), "quizzes": db.query(QuizResult).filter_by(owner_id=user.id).count(), "average_score": round(sum(result.percentage for result in db.query(QuizResult).filter_by(owner_id=user.id).all()) / max(1, db.query(QuizResult).filter_by(owner_id=user.id).count()))}}

@router.put("/profile")
def update_profile(body: ProfileBody, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.full_name, user.college, user.department = body.full_name.strip(), body.college.strip(), body.department.strip()
    db.commit(); db.refresh(user)
    return {"success": True, "user": payload(user)}

@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    documents = db.query(Document).filter_by(owner_id=user.id).count()
    questions = db.query(ChatMessage).join(ChatMessage.session).filter_by(owner_id=user.id, role="user").count()
    results = db.query(QuizResult).filter_by(owner_id=user.id).all()
    return {"success": True, "stats": {"courses": db.query(Course).count(), "materials": documents, "questions": questions, "quiz_score": round(sum(r.percentage for r in results) / max(1, len(results)))}, "activity": []}
