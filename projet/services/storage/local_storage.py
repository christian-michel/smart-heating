"""
local_storage.py

Stockage local de secours (fallback).
Synchronisation vers USB quand disponible.
Tous les fichiers CSV présents sur l'USB sont supprimés du stockage local.
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
        Synchronise TOUS les fichiers CSV locaux vers l'autre stockage (USB)
        et supprime les fichiers locaux dès qu'ils existent sur l'USB.
        """

        source_dir = self.base_path
        target_dir = other_storage.get_path()

        if not os.path.exists(target_dir):
            return

        synced_count = 0
        deleted_count = 0

        for filename in os.listdir(source_dir):

            if not filename.endswith(".csv"):
                continue

            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)

            try:
                # 1 Copier vers USB si nécessaire
                if not os.path.exists(target_file):
                    shutil.copy2(source_file, target_file)
                    print(f"Sync : {filename} copié vers USB")
                    synced_count += 1

                # 2 Supprimer localement dès que le fichier existe sur USB
                if os.path.exists(target_file):
                    os.remove(source_file)
                    print(f"Local : {filename} supprimé")
                    deleted_count += 1

            except Exception as e:
                print(f"Erreur sync {filename} : {e}")

        if synced_count or deleted_count:
            print(
                f"Synchronisation terminée : "
                f"{synced_count} fichier(s) copiés, "
                f"{deleted_count} fichier(s) supprimés localement."
            )