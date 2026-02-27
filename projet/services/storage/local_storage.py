"""
local_storage.py

Stockage local de secours (fallback).
Synchronisation vers USB quand disponible.
"""

import os
import shutil
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
        Copie les fichiers CSV locaux vers l'autre stockage (USB).
        Basée uniquement sur le nom de fichier pour éviter d'écraser.
        """

        source_dir = self.base_path
        target_dir = other_storage.get_path()

        # Vérifie que le stockage cible existe
        if not os.path.exists(target_dir):
            return

        for filename in os.listdir(source_dir):

            # On ne copie que les fichiers CSV
            if not filename.endswith(".csv"):
                continue

            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)

            # Si le fichier n'existe pas encore sur USB → on copie
            if not os.path.exists(target_file):
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"Sync : {filename} copié vers USB")
                except Exception as e:
                    print(f"Erreur sync {filename} : {e}")
