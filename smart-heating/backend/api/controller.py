"""
controller.py

Instance unique du AppController
"""

from backend.core.app_controller import AppController

controller = AppController()
controller.register_signals()
controller.start()
