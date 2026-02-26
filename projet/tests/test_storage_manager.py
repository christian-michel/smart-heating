"""
test_storage_manager.py

Tests pour vérifier le comportement du StorageManager.
"""

from services.storage_manager import StorageManager
from services.storage.usb_storage import USBStorage
from services.storage.local_storage import LocalStorage


def test_storage_manager_uses_local_if_usb_unavailable(monkeypatch):
    """
    Vérifie que le stockage local est utilisé si l'USB est absent.
    """

    monkeypatch.setattr(USBStorage, "is_available", lambda self: False)

    manager = StorageManager()
    active = manager.get_active_storage()

    assert isinstance(active, LocalStorage)


def test_storage_manager_uses_usb_if_available(monkeypatch):
    """
    Vérifie que l'USB est utilisé s'il est disponible.
    """

    monkeypatch.setattr(USBStorage, "is_available", lambda self: True)

    manager = StorageManager()
    active = manager.get_active_storage()

    assert isinstance(active, USBStorage)
