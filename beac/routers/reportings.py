from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os, uuid

from config import UPLOADS_DIR, UPLOAD_ALLOWED, UPLOAD_MAX_B, UPLOAD_MAX_MB
from core.database import get_db
from core.logger import get_logger
from models.models import Reporting
from schemas.schemas import ReportingOut, MessageResponse

log    = get_logger(__name__)
router = APIRouter(prefix="/api/reportings", tags=["Reporting"])

def _svc_dir(service: str):
    d = UPLOADS_DIR / service
    d.mkdir(parents=True, exist_ok=True)
    return d

@router.get("/", response_model=List[ReportingOut])
def list_reportings(
    service: Optional[str] = Query(None, pattern="^(EM|SETSRC|SMP)$"),
    db: Session = Depends(get_db)
):
    q = db.query(Reporting)
    if service:
        q = q.filter(Reporting.service == service)
    return q.order_by(Reporting.uploaded_at.desc()).all()

@router.get("/{reporting_id}", response_model=ReportingOut)
def get_reporting(reporting_id: int, db: Session = Depends(get_db)):
    r = db.query(Reporting).filter(Reporting.id == reporting_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reporting introuvable")
    return r

@router.post("/upload", response_model=ReportingOut, status_code=201)
async def upload_reporting(
    service    : str        = Form(..., pattern="^(EM|SETSRC|SMP)$"),
    description: str        = Form(""),
    uploaded_by: str        = Form("Direction Générale"),
    file       : UploadFile = File(...),
    db         : Session    = Depends(get_db)
):
    ct = file.content_type or ""
    if ct not in UPLOAD_ALLOWED:
        raise HTTPException(status_code=415, detail=f"Type non autorisé : {ct}. Acceptés : PDF, Excel, CSV, Word")

    data = await file.read()
    if len(data) > UPLOAD_MAX_B:
        raise HTTPException(status_code=413, detail=f"Fichier trop volumineux. Limite : {UPLOAD_MAX_MB} Mo")

    ext       = UPLOAD_ALLOWED[ct]
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    dest      = _svc_dir(service) / safe_name

    with open(dest, "wb") as f:
        f.write(data)

    record = Reporting(
        service=service, filename=safe_name,
        original_name=file.filename or safe_name,
        file_type=ext, file_size=len(data),
        description=description, uploaded_by=uploaded_by,
    )
    db.add(record); db.commit(); db.refresh(record)
    log.info(f"Upload → {service}/{safe_name} ({len(data)//1024} Ko) par {uploaded_by}")
    return record

@router.get("/{reporting_id}/download")
def download_reporting(reporting_id: int, db: Session = Depends(get_db)):
    r = db.query(Reporting).filter(Reporting.id == reporting_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reporting introuvable")
    path = _svc_dir(r.service) / r.filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le serveur")
    log.info(f"Download → {r.original_name}")
    return FileResponse(path=str(path), filename=r.original_name, media_type="application/octet-stream")

@router.delete("/{reporting_id}", response_model=MessageResponse)
def delete_reporting(reporting_id: int, db: Session = Depends(get_db)):
    r = db.query(Reporting).filter(Reporting.id == reporting_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reporting introuvable")
    path = _svc_dir(r.service) / r.filename
    if path.exists():
        path.unlink()
    db.delete(r); db.commit()
    log.info(f"Reporting supprimé → id={reporting_id}")
    return {"message": "Reporting supprimé", "id": reporting_id}
