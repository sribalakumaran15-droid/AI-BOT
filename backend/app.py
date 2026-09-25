import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import FRONTEND_URL
from backend.database.db import Base, SessionLocal, engine
from backend.models.models import Course
from backend.routes import auth, chat, courses, documents, quiz, users

app = FastAPI(title="StudyAI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(users.router); app.include_router(courses.router); app.include_router(documents.router); app.include_router(chat.router); app.include_router(quiz.router)

@app.exception_handler(Exception)
async def generic_error(request: Request, exception: Exception):
    return JSONResponse(status_code=500, content={"success": False, "message": "Something went wrong. Please try again."})

@app.get("/api/health")
def health(): return {"success": True, "message": "StudyAI API is running"}

def seed_courses():
    Base.metadata.create_all(bind=engine)
    data_path = Path(__file__).resolve().parents[1] / "data" / "courses.json"
    with SessionLocal() as db:
        if db.query(Course).count() == 0:
            for course in json.loads(data_path.read_text(encoding="utf-8")):
                db.add(Course(name=course["name"], description=course["description"], important_topics=json.dumps(course["important_topics"]), syllabus=json.dumps(course["syllabus"])))
            db.commit()

seed_courses()
