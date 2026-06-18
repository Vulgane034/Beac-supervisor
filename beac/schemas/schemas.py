from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DossierBase(BaseModel):
    titre   : str           = Field(..., min_length=2, max_length=255)
    service : str           = Field(..., pattern="^(EM|SETSRC|SMP)$")
    resp    : str           = Field(..., min_length=2, max_length=100)
    statut  : str           = Field("en_attente", pattern="^(en_attente|en_cours|traite|rejete)$")
    prio    : str           = Field("normale",     pattern="^(urgente|haute|normale|basse)$")
    echeance: str           = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    creation: str           = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    notes   : Optional[str] = ""

class DossierCreate(DossierBase):
    pass

class DossierUpdate(BaseModel):
    titre   : Optional[str] = Field(None, min_length=2, max_length=255)
    service : Optional[str] = Field(None, pattern="^(EM|SETSRC|SMP)$")
    resp    : Optional[str] = Field(None, min_length=2, max_length=100)
    statut  : Optional[str] = Field(None, pattern="^(en_attente|en_cours|traite|rejete)$")
    prio    : Optional[str] = Field(None, pattern="^(urgente|haute|normale|basse)$")
    echeance: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    creation: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    notes   : Optional[str] = None

class DossierOut(DossierBase):
    id        : int
    ref       : str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class KpiBase(BaseModel):
    name  : str            = Field(..., min_length=1, max_length=100)
    desc  : Optional[str]  = ""
    type  : str            = Field(..., min_length=1)
    filter: Optional[str]  = ""
    color : Optional[str]  = "#1A4A8A"
    active: Optional[bool] = True

class KpiCreate(KpiBase):
    pass

class KpiUpdate(BaseModel):
    name  : Optional[str]  = None
    desc  : Optional[str]  = None
    type  : Optional[str]  = None
    filter: Optional[str]  = None
    color : Optional[str]  = None
    active: Optional[bool] = None

class KpiOut(KpiBase):
    id        : int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class ReportingOut(BaseModel):
    id           : int
    service      : str
    filename     : str
    original_name: str
    file_type    : str
    file_size    : int
    description  : str
    uploaded_by  : str
    uploaded_at  : Optional[datetime] = None
    model_config = {"from_attributes": True}

class MessageResponse(BaseModel):
    message: str
    id     : Optional[int] = None
