"""
status.py

Route API : statut du système Smart Heating

- Protégée par token
- Retourne état complet du système
"""

from fastapi import APIRouter, Depends, HTTPException

from backend.api.controller import controller
from backend.api.dependencies import verify_token

router = APIRouter()


# ==========================
# === STATUS
# ==========================

@router.get("/status")
def get_status(auth=Depends(verify_token)):
    """
    Retourne l'état du système :
    - running
    - température actuelle
    - état chauffage
    - mode manuel
    """

    try:
        status = controller.get_status()

        # Log utile (debug)
        print(f"[API] /status → {status}")

        return status

    except Exception as e:
        print(f"[API] Erreur /status : {e}")
        raise HTTPException(status_code=500, detail="Internal server error")