from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.logger import get_logger
from models.models import KpiPersonnalise
from schemas.schemas import KpiCreate, KpiUpdate, KpiOut, MessageResponse

log    = get_logger(__name__)
router = APIRouter(prefix="/api/kpis", tags=["KPI"])

@router.get("/", response_model=List[KpiOut])
def list_kpis(db: Session = Depends(get_db)):
    return db.query(KpiPersonnalise).order_by(KpiPersonnalise.id).all()

@router.post("/", response_model=KpiOut, status_code=201)
def create_kpi(payload: KpiCreate, db: Session = Depends(get_db)):
    kpi = KpiPersonnalise(**payload.model_dump())
    db.add(kpi); db.commit(); db.refresh(kpi)
    log.info(f"KPI créé → id={kpi.id} name={kpi.name}")
    return kpi

@router.put("/{kpi_id}", response_model=KpiOut)
def update_kpi(kpi_id: int, payload: KpiUpdate, db: Session = Depends(get_db)):
    kpi = db.query(KpiPersonnalise).filter(KpiPersonnalise.id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI introuvable")
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(kpi, field, val)
    db.commit(); db.refresh(kpi)
    log.info(f"KPI modifié → id={kpi_id}")
    return kpi

@router.delete("/{kpi_id}", response_model=MessageResponse)
def delete_kpi(kpi_id: int, db: Session = Depends(get_db)):
    kpi = db.query(KpiPersonnalise).filter(KpiPersonnalise.id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI introuvable")
    db.delete(kpi); db.commit()
    log.info(f"KPI supprimé → id={kpi_id}")
    return {"message": "KPI supprimé", "id": kpi_id}
