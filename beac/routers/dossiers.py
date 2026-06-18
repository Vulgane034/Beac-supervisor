from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import date
import random, string

from config import SERVICE_PREFIXES
from core.database import get_db
from core.logger import get_logger
from models.models import Dossier
from schemas.schemas import DossierCreate, DossierUpdate, DossierOut, MessageResponse

log    = get_logger(__name__)
router = APIRouter(prefix="/api/dossiers", tags=["Dossiers"])

def _gen_ref(service: str, db: Session) -> str:
    prefix = SERVICE_PREFIXES.get(service, "XX")
    year   = date.today().year
    while True:
        suffix = ''.join(random.choices(string.digits, k=4))
        ref = f"{prefix}-{year}-{suffix}"
        if not db.query(Dossier).filter(Dossier.ref == ref).first():
            return ref

@router.get("/", response_model=List[DossierOut])
def list_dossiers(
    search : Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    statut : Optional[str] = Query(None),
    prio   : Optional[str] = Query(None),
    db     : Session       = Depends(get_db)
):
    q = db.query(Dossier)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Dossier.ref.ilike(like), Dossier.titre.ilike(like), Dossier.resp.ilike(like)))
    if service: q = q.filter(Dossier.service == service)
    if statut:  q = q.filter(Dossier.statut  == statut)
    if prio:    q = q.filter(Dossier.prio    == prio)
    results = q.order_by(Dossier.id.desc()).all()
    log.debug(f"list_dossiers → {len(results)} résultat(s)")
    return results

@router.get("/{dossier_id}", response_model=DossierOut)
def get_dossier(dossier_id: int, db: Session = Depends(get_db)):
    d = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier introuvable")
    return d

@router.post("/", response_model=DossierOut, status_code=201)
def create_dossier(payload: DossierCreate, db: Session = Depends(get_db)):
    d = Dossier(**payload.model_dump(), ref=_gen_ref(payload.service, db))
    db.add(d); db.commit(); db.refresh(d)
    log.info(f"Dossier créé → {d.ref} | {d.service} | {d.resp}")
    return d

@router.put("/{dossier_id}", response_model=DossierOut)
def update_dossier(dossier_id: int, payload: DossierUpdate, db: Session = Depends(get_db)):
    d = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier introuvable")
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(d, field, val)
    db.commit(); db.refresh(d)
    log.info(f"Dossier modifié → {d.ref}")
    return d

@router.patch("/{dossier_id}/statut", response_model=DossierOut)
def update_statut(
    dossier_id: int,
    statut: str = Query(..., pattern="^(en_attente|en_cours|traite|rejete)$"),
    db: Session = Depends(get_db)
):
    d = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier introuvable")
    old = d.statut; d.statut = statut
    db.commit(); db.refresh(d)
    log.info(f"Statut → {d.ref} : {old} → {statut}")
    return d

@router.delete("/{dossier_id}", response_model=MessageResponse)
def delete_dossier(dossier_id: int, db: Session = Depends(get_db)):
    d = db.query(Dossier).filter(Dossier.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier introuvable")
    ref = d.ref
    db.delete(d); db.commit()
    log.info(f"Dossier supprimé → {ref}")
    return {"message": "Dossier supprimé", "id": dossier_id}
