from fastapi import APIRouter, Depends
from backend.api.controller import controller
from backend.api.dependencies import verify_token

router = APIRouter()

@router.get("/status")
def get_status(auth=Depends(verify_token)):
    return controller.get_status()
