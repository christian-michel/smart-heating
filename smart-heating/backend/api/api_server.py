"""
api_server.py

Entrypoint FastAPI

- Initialise l'API
- Enregistre toutes les routes
- Architecture modulaire (routes séparées)
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routes
from backend.api.routes import status, heating, mode, system, ui, temperature

app = FastAPI(title="Smart Heating API")

# ==========================
# === CORS
# ==========================
# Nécessaire pour piloter l'API depuis un navigateur (app web/mobile
# servie sur une autre origine que RASPBERRY_IP:8000).
#
# Par défaut, autorise tout ("*") pour ne pas casser l'usage en LAN.
# Pour un accès exposé sur Internet, fixe CORS_ALLOWED_ORIGINS dans le
# .env à une liste d'origines séparées par des virgules, ex :
#   CORS_ALLOWED_ORIGINS=https://mon-app.exemple.com
_cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "*")
_cors_origins = ["*"] if _cors_env.strip() == "*" else [
    o.strip() for o in _cors_env.split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# === ROUTES REGISTRATION
# ==========================

app.include_router(status.router)
app.include_router(heating.router)
app.include_router(mode.router)
app.include_router(system.router)
app.include_router(ui.router)
app.include_router(temperature.router)