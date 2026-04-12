from fastapi import APIRouter, Depends
from backend.api.controller import controller
from backend.api.dependencies import verify_token

router = APIRouter()

@router.post("/manual/{state}")
def set_manual_mode(state: bool, auth=Depends(verify_token)):
    success = controller.set_manual_mode(state)

    if success:
        return {"manual_mode": state}
    return {"error": "thermostat not ready"}
