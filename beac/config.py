"""
BEAC — Configuration centralisée
Modifier ce fichier pour adapter l'environnement.
"""
import os
from pathlib import Path

# ── Chemins ───────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent
UPLOADS_DIR  = BASE_DIR / "uploads"
STATIC_DIR   = BASE_DIR / "static"
LOGS_DIR     = BASE_DIR / "logs"

for _d in [UPLOADS_DIR/"EM", UPLOADS_DIR/"SETSRC", UPLOADS_DIR/"SMP",
           STATIC_DIR, LOGS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── Application ───────────────────────────────────────────
APP_TITLE       = "BEAC — Supervision des Dossiers"
APP_DESCRIPTION = "API REST — Plateforme BEAC de suivi des dossiers administratifs (Zone CEMAC)"
APP_VERSION     = "1.0.0"
APP_ENV         = os.getenv("BEAC_ENV", "development")

# ── Serveur ───────────────────────────────────────────────
SERVER_HOST   = os.getenv("BEAC_HOST", "0.0.0.0")
SERVER_PORT   = int(os.getenv("BEAC_PORT", "8000"))
SERVER_RELOAD = APP_ENV == "development"

# ── Base de données ───────────────────────────────────────
DATABASE_URL = os.getenv("BEAC_DATABASE_URL", f"sqlite:///{BASE_DIR}/beac.db")
# Production PostgreSQL :
# DATABASE_URL = "postgresql://user:password@localhost:5432/beac"

# ── CORS ──────────────────────────────────────────────────
CORS_ORIGINS = ["*"] if APP_ENV == "development" else \
               os.getenv("BEAC_CORS_ORIGINS", "http://localhost:8000").split(",")

# ── Upload fichiers ───────────────────────────────────────
UPLOAD_MAX_MB   = int(os.getenv("BEAC_UPLOAD_MAX_MB", "20"))
UPLOAD_MAX_B    = UPLOAD_MAX_MB * 1024 * 1024
UPLOAD_ALLOWED  = {
    "application/pdf"                                                           : "pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"         : "xlsx",
    "application/vnd.ms-excel"                                                  : "xls",
    "text/csv"                                                                  : "csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"   : "docx",
    "application/msword"                                                        : "doc",
}

# ── Logging ───────────────────────────────────────────────
LOG_LEVEL        = os.getenv("BEAC_LOG_LEVEL", "INFO")
LOG_MAX_BYTES    = 5 * 1024 * 1024   # 5 Mo
LOG_BACKUP_COUNT = 10
LOG_FORMAT       = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
LOG_DATE_FORMAT  = "%Y-%m-%d %H:%M:%S"
LOG_FILE_APP     = LOGS_DIR / "beac_app.log"
LOG_FILE_ACCESS  = LOGS_DIR / "beac_access.log"
LOG_FILE_ERROR   = LOGS_DIR / "beac_error.log"

# ── Référentiels métier ───────────────────────────────────
SERVICES_VALIDES  = ["EM", "SETSRC", "SMP"]
STATUTS_VALIDES   = ["en_attente", "en_cours", "traite", "rejete"]
PRIORITES_VALIDES = ["urgente", "haute", "normale", "basse"]
SERVICE_PREFIXES  = {"EM": "EM", "SETSRC": "ST", "SMP": "SM"}
