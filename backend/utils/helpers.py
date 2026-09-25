import json
from pathlib import Path
from fastapi import HTTPException, UploadFile
from backend.config import MAX_UPLOAD_BYTES

ALLOWED_TYPES = {".pdf", ".docx", ".txt"}

def json_load(value: str, fallback=None):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback if fallback is not None else []

def validate_upload(upload: UploadFile, size: int):
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")
    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Files must be smaller than 10 MB.")
