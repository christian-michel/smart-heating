"""
dependencies.py

Gestion de l'authentification API (version PRO)

- Support Bearer Token
- Logs debug utiles
- Gestion erreurs robuste
- Compatible systemd + .env
"""

import os
from fastapi import Header, HTTPException


# ==========================
# === CONFIG TOKEN
# ==========================

API_TOKEN = os.getenv("API_TOKEN", "changeme")

print(f"[AUTH] Token attendu chargé (longueur={len(API_TOKEN)})")


# ==========================
# === VERIFY TOKEN
# ==========================

def verify_token(authorization: str = Header(None)):
    """
    Vérifie le header Authorization: Bearer <token>
    """

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    # Nettoyage (important)
    authorization = authorization.strip()

    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid auth format")

    # Debug utile (non sensible)
    print(f"[AUTH] Reçu scheme={scheme}")

    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    if token.strip() != API_TOKEN:
        print(f"[AUTH] Token invalide reçu (longueur={len(token.strip())})")
        raise HTTPException(status_code=403, detail="Invalid token")

    # Succès
    return True