import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import Quiz, QuizQuestion, QuizResult, User
from backend.services.quiz_service import create_questions
from backend.utils.auth import current_user

router = APIRouter(prefix="/api/quiz", tags=["quiz"])
class GenerateBody(BaseModel):
    course: str
    topic: str
    difficulty: str = "Easy"
    count: int = Field(default=5, ge=1, le=15)
class SubmitBody(BaseModel):
    quiz_id: int
    answers: list[str]

@router.post("/generate")
def generate(body: GenerateBody, user: User = Depends(current_user), db: Session = Depends(get_db)):
    quiz = Quiz(owner_id=user.id, course=body.course, topic=body.topic, difficulty=body.difficulty); db.add(quiz); db.flush()
    for question in create_questions(body.course, body.topic, body.difficulty, body.count):
        db.add(QuizQuestion(quiz_id=quiz.id, prompt=question["prompt"], options=json.dumps(question["options"]), answer=question["answer"], explanation=question["explanation"]))
    db.commit(); db.refresh(quiz)
    return {"success": True, "quiz": {"id": quiz.id, "course": quiz.course, "topic": quiz.topic, "difficulty": quiz.difficulty, "questions": [{"id": q.id, "prompt": q.prompt, "options": json.loads(q.options)} for q in quiz.questions]}}

@router.post("/submit")
def submit(body: SubmitBody, user: User = Depends(current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter_by(id=body.quiz_id, owner_id=user.id).first()
    if not quiz: raise HTTPException(404, "Quiz not found.")
    correct = sum(answer == question.answer for answer, question in zip(body.answers, quiz.questions))
    total = len(quiz.questions); percentage = round(correct / max(1, total) * 100)
    db.add(QuizResult(owner_id=user.id, quiz_id=quiz.id, score=correct, total=total, percentage=percentage)); db.commit()
    return {"success": True, "score": correct, "total": total, "percentage": percentage, "explanations": [{"answer": q.answer, "explanation": q.explanation} for q in quiz.questions]}

@router.get("/history")
def quiz_history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"success": True, "history": [{"score": r.score, "total": r.total, "percentage": r.percentage, "created_at": r.created_at.isoformat()} for r in db.query(QuizResult).filter_by(owner_id=user.id).order_by(QuizResult.created_at.desc()).all()]}
