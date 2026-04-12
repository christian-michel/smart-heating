"""
api_server.py

API HTTP pour piloter Smart Heating à distance.

Version PRO :
- Utilise AppController uniquement (pas d'accès direct thermostat)
- Thread-safe
- Compatible smartphone / UI web
"""

from fastapi import FastAPI
from backend.core.app_controller import AppController

# ==========================
# === INIT APP
# ==========================

app = FastAPI(title="Smart Heating API")

# Singleton global
controller = AppController()
controller.register_signals()
controller.start()


# ==========================
# === STATUS
# ==========================

@app.get("/status")
def get_status():
    """
    Retourne l'état complet du système.
    """
    return controller.get_status()


# ==========================
# === HEATING CONTROL
# ==========================

@app.post("/heating/{state}")
def set_heating(state: bool):
    """
    Force ON/OFF du chauffage.
    """
    success = controller.force_heating(state)

    if success:
        return {"heating": state}
    return {"error": "thermostat not ready"}


# ==========================
# === MODE CONTROL
# ==========================

@app.post("/manual/{state}")
def set_manual_mode(state: bool):
    """
    Active / désactive le mode manuel.
    """
    success = controller.set_manual_mode(state)

    if success:
        return {"manual_mode": state}
    return {"error": "thermostat not ready"}


# ==========================
# === SYSTEM CONTROL
# ==========================

@app.post("/restart")
def restart():
    """
    Redémarre proprement le système.
    """
    controller.restart()
    return {"status": "restarted"}


@app.post("/stop")
def stop():
    """
    Arrêt propre du système.
    """
    controller.stop()
    return {"status": "stopped"}


@app.post("/start")
def start():
    """
    Démarrage du système.
    """
    controller.start()
    return {"status": "started"}