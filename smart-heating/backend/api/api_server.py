"""
api_server.py

Entrypoint FastAPI

- Initialise l'API
- Enregistre toutes les routes
- Architecture modulaire (routes séparées)
"""

from fastapi import FastAPI

# Import des routes
from backend.api.routes import status, heating, mode, system, ui, temperature

app = FastAPI(title="Smart Heating API")

# ==========================
# === ROUTES REGISTRATION
# ==========================

app.include_router(status.router)
app.include_router(heating.router)
app.include_router(mode.router)
app.include_router(system.router)
app.include_router(ui.router)
app.include_router(temperature.router)