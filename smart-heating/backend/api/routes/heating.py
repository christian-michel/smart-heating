from fastapi import APIRouter, Depends
from backend.api.controller import controller
from backend.api.dependencies import verify_token

router = APIRouter()

@router.post("/heating/{state}")
def set_heating(state: bool, auth=Depends(verify_token)):
    success = controller.force_heating(state)

    if success:
        return {"heating": state}

    if controller.thermostat and not controller.thermostat.can_switch():
        return {"error": "switch rejected: anti short-cycle protection active"}

    return {"error": "thermostat not ready"}