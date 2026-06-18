# ==============================================================
#  BEAC — Orchestrateur de démarrage
#  Usage : clic-droit > "Exécuter avec PowerShell"
#          ou dans un terminal PowerShell : .\start.ps1
# ==============================================================
param(
    [string]$Host = "127.0.0.1",
    [int]$Port    = 8000,
    [string]$Env  = "development"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Utilitaires console ────────────────────────────────────
function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   BEAC — Supervision des Dossiers  v1.0.0   ║" -ForegroundColor Cyan
    Write-Host "║   Banque des États de l'Afrique Centrale     ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}
function Write-Step([string]$msg) { Write-Host "  ► $msg" -ForegroundColor Yellow }
function Write-OK([string]$msg)   { Write-Host "  ✔ $msg" -ForegroundColor Green  }
function Write-Warn([string]$msg) { Write-Host "  ⚠ $msg" -ForegroundColor DarkYellow }
function Write-Fail([string]$msg) {
    Write-Host ""
    Write-Host "  ✖ ERREUR : $msg" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Appuyez sur une touche pour fermer..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# ── Répertoire de travail = dossier du script ──────────────
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $PROJECT_ROOT
Write-Banner
Write-Host "  Répertoire projet : $PROJECT_ROOT" -ForegroundColor Gray
Write-Host ""

# ── 1. Python ──────────────────────────────────────────────
Write-Step "Vérification de Python..."
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -lt 10) { Write-Fail "Python 3.10+ requis. Détecté : $ver" }
            $python = $cmd
            Write-OK "$ver détecté ($cmd)"
            break
        }
    } catch {}
}
if (-not $python) { Write-Fail "Python introuvable. Installez Python 3.10+ et ajoutez-le au PATH." }

# ── 2. Vérification main.py ────────────────────────────────
Write-Step "Vérification des fichiers du projet..."
if (-not (Test-Path (Join-Path $PROJECT_ROOT "main.py"))) {
    Write-Fail "main.py introuvable dans : $PROJECT_ROOT`nAssurez-vous de lancer start.ps1 depuis le dossier 'beac'."
}
Write-OK "Fichiers projet OK"

# ── 3. Environnement virtuel ───────────────────────────────
Write-Step "Environnement virtuel Python (.venv)..."
$VENV = Join-Path $PROJECT_ROOT ".venv"
if (-not (Test-Path $VENV)) {
    Write-Host "     Création du venv..." -ForegroundColor Gray
    & $python -m venv $VENV
    if ($LASTEXITCODE -ne 0) { Write-Fail "Impossible de créer le venv." }
}

# Chemins binaires selon OS
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $PIP      = Join-Path $VENV "Scripts\pip.exe"
    $PYTHON_V = Join-Path $VENV "Scripts\python.exe"
    $UVICORN  = Join-Path $VENV "Scripts\uvicorn.exe"
} else {
    $PIP      = Join-Path $VENV "bin/pip"
    $PYTHON_V = Join-Path $VENV "bin/python"
    $UVICORN  = Join-Path $VENV "bin/uvicorn"
}

if (-not (Test-Path $PYTHON_V)) {
    Write-Fail "Python dans le venv introuvable. Supprimez le dossier .venv et relancez."
}
Write-OK "Venv OK : $VENV"

# ── 4. Dépendances ─────────────────────────────────────────
Write-Step "Installation / vérification des dépendances..."
$REQ = Join-Path $PROJECT_ROOT "requirements.txt"
if (Test-Path $REQ) {
    & $PIP install -r $REQ --quiet --upgrade 2>&1 | Out-Null
    Write-OK "Dépendances installées (requirements.txt)"
} else {
    & $PIP install fastapi "uvicorn[standard]" sqlalchemy pydantic python-multipart aiofiles --quiet 2>&1 | Out-Null
    Write-OK "Dépendances de base installées"
}

# ── 5. Structure des dossiers ──────────────────────────────
Write-Step "Vérification de la structure..."
$dirs = @("static","uploads\EM","uploads\SETSRC","uploads\SMP","logs")
foreach ($d in $dirs) {
    $path = Join-Path $PROJECT_ROOT $d
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "     Créé : $d" -ForegroundColor Gray
    }
}
Write-OK "Structure des dossiers OK"

# ── 6. Frontend ────────────────────────────────────────────
Write-Step "Vérification du frontend..."
$FRONTEND = Join-Path $PROJECT_ROOT "static\index.html"
if (-not (Test-Path $FRONTEND)) {
    Write-Warn "static\index.html absent — déposez le fichier frontend dans static\ et nommez-le index.html"
} else {
    Write-OK "Frontend OK : static\index.html"
}

# ── 7. Test d'import Python ────────────────────────────────
Write-Step "Validation des modules Python..."
$check = & $PYTHON_V -c "import sys; sys.path.insert(0,'.'); import main; print('OK')" 2>&1
if ($check -notmatch "OK") {
    Write-Host ""
    Write-Host "  Détail de l'erreur :" -ForegroundColor Red
    Write-Host $check -ForegroundColor Red
    Write-Fail "Les modules Python ne s'importent pas correctement. Consultez l'erreur ci-dessus."
}
Write-OK "Modules Python OK"

# ── 8. Libération du port ──────────────────────────────────
Write-Step "Vérification du port $Port..."
try {
    $connections = netstat -ano 2>$null | Select-String ":$Port\s" | Select-String "LISTENING"
    if ($connections) {
        Write-Warn "Port $Port occupé — libération en cours..."
        foreach ($line in $connections) {
            $parts = $line.ToString().Trim() -split '\s+'
            $pid   = $parts[-1]
            if ($pid -match '^\d+$' -and $pid -ne "0") {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
                Write-Host "     PID $pid arrêté" -ForegroundColor Gray
            }
        }
        Start-Sleep -Seconds 1
    }
} catch {}
Write-OK "Port $Port disponible"

# ── 9. Démarrage ───────────────────────────────────────────
$APP_URL = "http://${Host}:${Port}"
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   Serveur BEAC en démarrage...               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Application  →  $APP_URL" -ForegroundColor White
Write-Host "  API Swagger  →  $APP_URL/docs" -ForegroundColor White
Write-Host "  Logs         →  $PROJECT_ROOT\logs\" -ForegroundColor White
Write-Host ""
Write-Host "  Ctrl+C pour arrêter le serveur." -ForegroundColor Gray
Write-Host ""

# Ouvrir le navigateur après 3 secondes
$url = $APP_URL
Start-Job -ScriptBlock {
    param($u)
    Start-Sleep -Seconds 3
    Start-Process $u
} -ArgumentList $url | Out-Null

# ── 10. Lancement uvicorn ──────────────────────────────────
$env:BEAC_ENV  = $Env
$env:BEAC_HOST = $Host
$env:BEAC_PORT = "$Port"

# --app-dir garantit que uvicorn trouve main.py même si le CWD diffère
& $UVICORN main:app `
    --host $Host `
    --port $Port `
    --reload `
    --reload-dir $PROJECT_ROOT `
    --log-level info
