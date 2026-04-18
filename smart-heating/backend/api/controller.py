"""
controller.py

Instance globale unique du AppController.

Version PRO stable :
- Singleton simple
- Compatible FastAPI
- Évite toute confusion get_controller vs controller
"""

from backend.core.app_controller import AppController

print("[API] Initialisation du controller global...")

controller = AppController()
controller.register_signals()
controller.start()

print("[API] Controller prêt")