"""
BEAC — Supervision des Dossiers
Entrypoint principal FastAPI
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import (APP_TITLE, APP_DESCRIPTION, APP_VERSION, APP_ENV,
                    CORS_ORIGINS, STATIC_DIR, UPLOADS_DIR)
from core.database import engine, Base
from core.logger import get_logger, get_access_logger
from models.models import Dossier, KpiPersonnalise, Reporting  # noqa
from routers import dossiers, kpis, reportings

log        = get_logger(__name__)
access_log = get_access_logger()

# ── Initialisation DB ──────────────────────────────────────
Base.metadata.create_all(bind=engine)
log.info(f"DB initialisée — env={APP_ENV}")

# ── Application ────────────────────────────────────────────
app = FastAPI(
    title       = APP_TITLE,
    description = APP_DESCRIPTION,
    version     = APP_VERSION,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS ───────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = CORS_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Middleware logging HTTP ────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        log.error(f"Erreur non gérée : {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})
    ms = (time.perf_counter() - t0) * 1000
    access_log.info(
        f"{request.method} {request.url.path} → {response.status_code} "
        f"[{ms:.1f}ms] {request.client.host if request.client else '-'}"
    )
    return response

# ── Routers API ────────────────────────────────────────────
app.include_router(dossiers.router)
app.include_router(kpis.router)
app.include_router(reportings.router)
log.info("Routers enregistrés : /api/dossiers  /api/kpis  /api/reportings")

# ── Fichiers uploadés ──────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ── Frontend statique ──────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Route racine → frontend ────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"status": "ok", "app": APP_TITLE, "version": APP_VERSION,
                         "ui": "/static/beac-suivi-dossiers.html", "docs": "/docs"})

# ── Health ─────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "env": APP_ENV, "version": APP_VERSION}

log.info(f"BEAC API prête — {APP_TITLE} v{APP_VERSION}")
