# BEAC — Supervision des Dossiers Administratifs

Plateforme de suivi des dossiers pour la Banque des États de l'Afrique Centrale (BEAC), Zone CEMAC.

---

## Architecture du projet

```
beac/
│
├── start.ps1                  ← Orchestrateur PowerShell (point d'entrée)
├── main.py                    ← Entrypoint FastAPI
├── config.py                  ← Configuration centralisée (ports, DB, logs, CORS...)
├── requirements.txt
│
├── static/
│   └── index.html             ← Frontend (servi par FastAPI à la racine)
│
├── uploads/                   ← Fichiers déposés par les services
│   ├── EM/
│   ├── SETSRC/
│   └── SMP/
│
├── logs/                      ← Logs auto-générés avec rotation
│   ├── beac_app.log
│   ├── beac_access.log
│   └── beac_error.log
│
├── beac.db                    ← Base SQLite (créée au premier lancement)
│
├── core/
│   ├── database.py            ← Engine SQLAlchemy + session
│   └── logger.py              ← Générateur de logs centralisé (rotation auto)
│
├── models/
│   └── models.py              ← Tables : Dossier, KpiPersonnalise, Reporting
│
├── schemas/
│   └── schemas.py             ← Schémas Pydantic (validation entrées/sorties)
│
└── routers/
    ├── dossiers.py            ← CRUD complet dossiers
    ├── kpis.py                ← CRUD KPI personnalisés
    └── reportings.py          ← Upload / Download / Suppression fichiers
```

---

## Démarrage rapide

### Prérequis
- Python 3.10 ou supérieur
- PowerShell 5.1+ (Windows) — inclus nativement

### Lancement (une seule commande)

**Double-cliquez** sur `start.ps1` ou dans un terminal PowerShell :

```powershell
.\start.ps1
```

Le script :
1. Vérifie Python
2. Crée l'environnement virtuel `.venv`
3. Installe les dépendances automatiquement
4. Crée les dossiers nécessaires
5. Libère le port si occupé
6. Démarre le serveur FastAPI
7. Ouvre le navigateur automatiquement

### URLs après démarrage

| Accès | URL |
|-------|-----|
| **Application** | http://127.0.0.1:8000 |
| **Documentation API (Swagger)** | http://127.0.0.1:8000/docs |
| **Documentation API (ReDoc)** | http://127.0.0.1:8000/redoc |
| **Health check** | http://127.0.0.1:8000/health |

---

## Configuration (config.py)

Toute la configuration est centralisée dans `config.py` :

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Hôte d'écoute |
| `SERVER_PORT` | `8000` | Port du serveur |
| `DATABASE_URL` | SQLite local | Connexion base de données |
| `APP_ENV` | `development` | Environnement (`development` / `production`) |
| `UPLOAD_MAX_MB` | `20` | Taille max upload fichiers |
| `LOG_LEVEL` | `INFO` | Niveau de log |
| `CORS_ORIGINS` | `["*"]` en dev | Origines CORS autorisées |

Les paramètres peuvent être surchargés via variables d'environnement :

```powershell
$env:BEAC_PORT = "9000"
$env:BEAC_ENV  = "production"
$env:BEAC_LOG_LEVEL = "DEBUG"
.\start.ps1
```

---

## API Reference

### Dossiers — `/api/dossiers`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/dossiers/` | Liste (filtres : `search`, `service`, `statut`, `prio`) |
| `GET` | `/api/dossiers/{id}` | Détail d'un dossier |
| `POST` | `/api/dossiers/` | Créer un dossier |
| `PUT` | `/api/dossiers/{id}` | Modifier un dossier |
| `PATCH` | `/api/dossiers/{id}/statut?statut=...` | Changer le statut uniquement |
| `DELETE` | `/api/dossiers/{id}` | Supprimer un dossier |

**Valeurs métier :**
- `service` : `EM` · `SETSRC` · `SMP`
- `statut` : `en_attente` · `en_cours` · `traite` · `rejete`
- `prio` : `urgente` · `haute` · `normale` · `basse`

### KPI Personnalisés — `/api/kpis`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/kpis/` | Liste des KPI |
| `POST` | `/api/kpis/` | Créer un KPI |
| `PUT` | `/api/kpis/{id}` | Modifier un KPI |
| `DELETE` | `/api/kpis/{id}` | Supprimer un KPI |

### Reportings / Fichiers — `/api/reportings`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/reportings/` | Liste (filtre : `?service=EM`) |
| `POST` | `/api/reportings/upload` | Upload fichier (multipart/form-data) |
| `GET` | `/api/reportings/{id}/download` | Télécharger un fichier |
| `DELETE` | `/api/reportings/{id}` | Supprimer un fichier |

**Paramètres upload (form-data) :**
```
service       : EM | SETSRC | SMP    (requis)
file          : fichier              (requis)
description   : texte libre         (optionnel)
uploaded_by   : nom du déposant     (optionnel)
```
Formats acceptés : PDF, Excel (.xlsx/.xls), CSV, Word (.docx/.doc) — max 20 Mo

---

## Logs

Trois fichiers de log avec rotation automatique (max 5 Mo × 10 fichiers) :

| Fichier | Contenu |
|---------|---------|
| `logs/beac_app.log` | Toutes les traces applicatives |
| `logs/beac_access.log` | Requêtes HTTP (méthode, route, statut, durée) |
| `logs/beac_error.log` | Erreurs uniquement |

---

## Migration vers PostgreSQL (production)

Dans `config.py`, remplacer :
```python
DATABASE_URL = "sqlite:///./beac.db"
```
par :
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/beac"
```
Et installer le driver : `pip install psycopg2-binary`

---

## Arrêt du serveur

`Ctrl + C` dans le terminal PowerShell.
