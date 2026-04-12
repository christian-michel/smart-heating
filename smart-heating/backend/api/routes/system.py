from fastapi import APIRouter, Depends
from backend.api.controller import controller
from backend.api.dependencies import verify_token

router = APIRouter()

@router.post("/restart")
def restart(auth=Depends(verify_token)):
    controller.restart()
    return {"status": "restarted"}


@router.post("/stop")
def stop(auth=Depends(verify_token)):
    controller.stop()
    return {"status": "stopped"}


@router.post("/start")
def start(auth=Depends(verify_token)):
    controller.start()
    return {"status": "started"}
