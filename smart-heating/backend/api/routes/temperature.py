"""
temperature.py

Gestion de la température de consigne (target_temperature)

Responsabilités :
- Lire la consigne utilisateur
- Modifier la consigne
- Interface API pour frontend
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.controller import controller
from backend.api.dependencies import verify_token

router = APIRouter()


# ==========================
# === SCHEMA
# ==========================

class TemperatureRequest(BaseModel):
    value: float = Field(..., ge=5.0, le=30.0)


# ==========================
# === GET TARGET TEMPERATURE
# ==========================

@router.get("/temperature/target")
def get_target(auth=Depends(verify_token)):
    """
    Retourne la température de consigne actuelle
    """

    try:
        status = controller.get_status()

        return {
            "target_temperature": status.get("target_temperature")
        }

    except Exception as e:
        print(f"[API] Erreur GET target temperature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================
# === SET TARGET TEMPERATURE
# ==========================

@router.post("/temperature/target")
def set_target(payload: TemperatureRequest, auth=Depends(verify_token)):
    """
    Définit la température de consigne
    """

    try:
        success = controller.set_target_temperature(payload.value)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Unable to set target temperature"
            )

        return {
            "status": "ok",
            "target_temperature": payload.value
        }

    except Exception as e:
        print(f"[API] Erreur SET target temperature: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")