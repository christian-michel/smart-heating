"""
local_storage.py

Stockage local de secours (fallback).
Toujours disponible.
"""

import os
from services.storage.base_storage import BaseStorage


class LocalStorage(BaseStorage):

    def __init__(self, base_path="data"):
        """
        base_path : dossier local où stocker les fichiers
        """
        self.base_path = base_path
        self._ensure_directory()

    def _ensure_directory(self):
        """
        Crée le dossier s'il n'existe pas.
        """
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def is_available(self) -> bool:
        """
        Le stockage local est toujours disponible.
        """
        return True

    def get_path(self) -> str:
        return self.base_path

    def sync(self, other_storage: BaseStorage):
        """
        Synchronisation future (non implémentée pour l'instant).
        """
        pass
