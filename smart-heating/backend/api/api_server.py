"""
api_server.py

Entrypoint FastAPI
"""

from fastapi import FastAPI

from backend.api.routes import status, heating, mode, system, ui

app = FastAPI(title="Smart Heating API")

# Routes
app.include_router(status.router)
app.include_router(heating.router)
app.include_router(mode.router)
app.include_router(system.router)
app.include_router(ui.router)