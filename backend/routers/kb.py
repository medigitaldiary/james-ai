from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from datetime import datetime

from services.ingestion import ingest_pdf
from db.vector_store import list_kb_files, delete_kb_file, get_kb_file

router = APIRouter(prefix="/kb", tags=["knowledge-base"])

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


class KBFileOut(BaseModel):
    id: str
    name: str
    size: int
    source: str
    url: str | None
    status: str
    uploaded_at: datetime


def _format_file(row: dict) -> KBFileOut:
    return KBFileOut(
        id=str(row["id"]),
        name=row["name"],
        size=row["size"],
        source=row["source"],
        url=row.get("url"),
        status=row["status"],
        uploaded_at=row["uploaded_at"],
    )


@router.post("/upload", response_model=KBFileOut)
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        kb_file = await ingest_pdf(
            file_bytes=file_bytes,
            filename=file.filename or "upload.pdf",
            file_size=len(file_bytes),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return _format_file(kb_file)


@router.get("/files", response_model=list[KBFileOut])
async def get_files():
    files = await list_kb_files()
    return [_format_file(f) for f in files]


@router.delete("/files/{file_id}", status_code=204)
async def remove_file(file_id: str):
    existing = await get_kb_file(file_id)
    if not existing:
        raise HTTPException(status_code=404, detail="File not found.")
    deleted = await delete_kb_file(file_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete file.")
