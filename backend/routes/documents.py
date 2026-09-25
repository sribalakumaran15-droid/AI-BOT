import json
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.config import UPLOAD_DIR
from backend.database.db import get_db
from backend.models.models import Document, DocumentChunk, User
from backend.services.document_service import clean_and_chunk, extract_text, retrieve
from backend.utils.auth import current_user
from backend.utils.helpers import validate_upload

router = APIRouter(prefix="/api/documents", tags=["documents"])
def serialize(document):
    return {"id": document.id, "filename": document.filename, "file_size": document.file_size, "status": document.status, "created_at": document.created_at.isoformat(), "chunks": len(document.chunks)}

@router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    content = await file.read()
    validate_upload(file, len(content))
    target = UPLOAD_DIR / f"{user.id}_{Path(file.filename).name}"
    target.write_bytes(content)
    text = extract_text(target)
    chunks = clean_and_chunk(text)
    if not chunks:
        raise HTTPException(422, "Unable to extract readable text from this document.")
    document = Document(owner_id=user.id, filename=file.filename, file_size=len(content))
    db.add(document); db.flush()
    db.add_all([DocumentChunk(document_id=document.id, content=chunk, chunk_index=index) for index, chunk in enumerate(chunks)])
    db.commit(); db.refresh(document)
    return {"success": True, "document": serialize(document)}

@router.get("")
def documents(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"success": True, "documents": [serialize(document) for document in db.query(Document).filter_by(owner_id=user.id).order_by(Document.created_at.desc()).all()]}

@router.delete("/{document_id}")
def delete_document(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter_by(id=document_id, owner_id=user.id).first()
    if not document: raise HTTPException(404, "Document not found.")
    db.delete(document); db.commit()
    return {"success": True}
