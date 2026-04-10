"""
local_storage.py

Stockage local de secours (fallback).

Philosophie :
- Toujours disponible
- Chemin centralisé via config.py
- Simple, robuste, prédictible

Synchronisation :
- Copie vers stockage cible (USB / Dropbox)
- Suppression locale une fois synchronisé
"""

import os
import shutil

from backend.config import LOCAL_STORAGE_PATH
from backend.services.storage.base_storage import BaseStorage


class LocalStorage(BaseStorage):

    def __init__(self, base_path=None):
        """
        Initialise le stockage local.

        Args:
            base_path (optionnel):
                Permet de surcharger le chemin (tests).
        """

        # Priorité au path override (tests)
        if base_path:
            self.base_path = base_path
        else:
            self.base_path = LOCAL_STORAGE_PATH

        self._ensure_directory()

    def _ensure_directory(self):
        """
        Crée le dossier s'il n'existe pas.
        """
        try:
            os.makedirs(self.base_path, exist_ok=True)
        except Exception as e:
            print(f"Erreur création dossier local : {e}")

    def is_available(self) -> bool:
        """
        Le stockage local est toujours disponible.
        """
        return True

    def get_path(self) -> str:
        """
        Retourne le chemin du stockage local.
        """
        return self.base_path

    def sync(self, other_storage: BaseStorage):
        """
        Synchronise les fichiers CSV vers un autre stockage.

        Comportement :
        1. Copie vers cible si absent
        2. Supprime local si copie réussie
        """

        source_dir = self.base_path
        target_dir = other_storage.get_path()

        if not os.path.exists(target_dir):
            print(f"Stockage cible indisponible : {target_dir}")
            return

        synced_count = 0
        deleted_count = 0

        for filename in os.listdir(source_dir):

            if not filename.endswith(".csv"):
                continue

            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)

            try:
                # === 1. Copie vers cible si nécessaire ===
                if not os.path.exists(target_file):
                    shutil.copy2(source_file, target_file)
                    print(f"[LocalStorage] Sync : {filename} → {target_dir}")
                    synced_count += 1

                # === 2. Suppression locale si présent sur cible ===
                if os.path.exists(target_file):
                    os.remove(source_file)
                    print(f"[LocalStorage] Suppression locale : {filename}")
                    deleted_count += 1

            except Exception as e:
                print(f"[LocalStorage] Erreur sync {filename} : {e}")

        if synced_count or deleted_count:
            print(
                f"[LocalStorage] Sync terminé : "
                f"{synced_count} copié(s), {deleted_count} supprimé(s)"
            )
