from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import ChatMessage, ChatSession, Document, User
from backend.services.ai_service import generate_answer
from backend.services.document_service import retrieve
from backend.utils.auth import current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])
class ChatBody(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: int | None = None

@router.post("")
def chat(body: ChatBody, user: User = Depends(current_user), db: Session = Depends(get_db)):
    session = db.get(ChatSession, body.session_id) if body.session_id else None
    if not session or session.owner_id != user.id:
        session = ChatSession(owner_id=user.id, title=body.question[:60]); db.add(session); db.flush()
    previous = [{"role": message.role, "content": message.content} for message in session.messages[-8:]]
    chunks = [chunk for document in db.query(Document).filter_by(owner_id=user.id).all() for chunk in document.chunks]
    retrieved = retrieve(chunks, body.question)
    answer = generate_answer(body.question, [{"text": chunk.content, "source": chunk.document.filename, "chunk": chunk.chunk_index} for chunk in retrieved], previous)
    db.add_all([ChatMessage(session_id=session.id, role="user", content=body.question), ChatMessage(session_id=session.id, role="assistant", content=answer)])
    db.commit()
    return {"success": True, "session_id": session.id, "answer": answer, "sources": [{"filename": chunk.document.filename, "chunk": chunk.chunk_index} for chunk in retrieved]}

@router.get("/history")
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter_by(owner_id=user.id).order_by(ChatSession.created_at.desc()).all()
    return {"success": True, "history": [{"id": session.id, "title": session.title, "messages": [{"role": m.role, "content": m.content} for m in session.messages]} for session in sessions]}
