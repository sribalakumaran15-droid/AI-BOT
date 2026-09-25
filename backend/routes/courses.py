import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import Course
from backend.utils.auth import current_user
from backend.utils.helpers import json_load

router = APIRouter(prefix="/api/courses", tags=["courses"])
def serialize(course):
    return {"id": course.id, "name": course.name, "description": course.description, "important_topics": json_load(course.important_topics), "syllabus": json_load(course.syllabus)}

@router.get("")
def courses(db: Session = Depends(get_db), user=Depends(current_user)):
    return {"success": True, "courses": [serialize(course) for course in db.query(Course).order_by(Course.name).all()]}

@router.get("/{course_id}")
def course(course_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    return {"success": True, "course": serialize(db.get(Course, course_id))}
