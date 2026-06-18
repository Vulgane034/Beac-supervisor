from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base

class Dossier(Base):
    __tablename__ = "dossiers"
    id         = Column(Integer, primary_key=True, index=True)
    ref        = Column(String(20), unique=True, nullable=False, index=True)
    titre      = Column(String(255), nullable=False)
    service    = Column(String(10), nullable=False)
    resp       = Column(String(100), nullable=False)
    statut     = Column(String(20), nullable=False, default="en_attente")
    prio       = Column(String(20), nullable=False, default="normale")
    echeance   = Column(String(10), nullable=False)
    creation   = Column(String(10), nullable=False)
    notes      = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class KpiPersonnalise(Base):
    __tablename__ = "kpis"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    desc       = Column(String(255), default="")
    type       = Column(String(50), nullable=False)
    filter     = Column(String(50), default="")
    color      = Column(String(20), default="#1A4A8A")
    active     = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reporting(Base):
    __tablename__ = "reportings"
    id            = Column(Integer, primary_key=True, index=True)
    service       = Column(String(10), nullable=False, index=True)
    filename      = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type     = Column(String(10), nullable=False)
    file_size     = Column(Integer, default=0)
    description   = Column(String(255), default="")
    uploaded_by   = Column(String(100), default="Direction Générale")
    uploaded_at   = Column(DateTime(timezone=True), server_default=func.now())
