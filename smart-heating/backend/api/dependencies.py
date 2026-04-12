"""
dependencies.py

Gestion de l'authentification API
"""

import os
from fastapi import Header, HTTPException

API_TOKEN = os.getenv("API_TOKEN", "changeme")


def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        scheme, token = authorization.split()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid auth format")

    if scheme.lower() != "bearer" or token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
