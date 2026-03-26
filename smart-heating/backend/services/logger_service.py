"""
logger_service.py

Gestion de l'enregistrement des données du thermostat
avec vérification dynamique du stockage.

Améliorations :
- Support d'un chemin custom (base_path) pour les tests
- Possibilité de désactiver la synchronisation (mode test)
- Toujours compatible avec StorageManager en production

Optimisation :
- Buffer RAM pour réduire les écritures
- Flush automatique
"""

import os
import csv
import time
from datetime import datetime

from backend.services.storage_manager import StorageManager


class LoggerService:

    def __init__(self, base_path: str = None, enable_sync: bool = True):
        """
        Initialise le logger.

        Args:
            base_path (str, optionnel):
                Permet de forcer un chemin de stockage (utile pour les tests).
                Si None → utilise StorageManager (comportement normal).

            enable_sync (bool):
                Active ou non la synchronisation (Dropbox, USB, etc.)
                Désactivé en test pour éviter effets de bord.
        """

        self.base_path_override = base_path
        self.enable_sync = enable_sync

        # StorageManager uniquement si pas de base_path custom
        self.storage_manager = None
        if self.base_path_override is None:
            self.storage_manager = StorageManager()

        self.session_filename = self._generate_session_filename()

        # --- BUFFER RAM ---
        self.buffer = []
        self.buffer_limit = 10
        self.flush_interval = 60 # secondes
        self.last_flush_time = time.time()

    def log(self, temperature: float, heating_state: bool, switch_state: bool):
        """
        Ajoute une ligne dans le buffer RAM.
        Déclenche un flush si nécessaire.
        """

        try:
            base_path = self._get_base_path()

            # Création dossier si nécessaire
            os.makedirs(base_path, exist_ok=True)

            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                temperature,
                heating_state,
                switch_state
            ]

            self.buffer.append(row)

            current_time = time.time()
            time_since_last_flush = current_time - self.last_flush_time

            if len(self.buffer) >= self.buffer_limit or time_since_last_flush >= self.flush_interval:

                self._flush_to_disk(base_path)
                self.last_flush_time = current_time

                # Synchronisation uniquement en mode prod
                if self.enable_sync and self.storage_manager:
                    self.storage_manager.refresh()

        except Exception as e:
            print(f"⚠ LoggerService.log : erreur -> {e}")

    def _get_base_path(self) -> str:
        """
        Détermine le chemin de stockage.
        """

        # Cas TEST → chemin forcé
        if self.base_path_override is not None:
            return self.base_path_override

        # Cas PROD → via StorageManager
        storage = self.storage_manager.get_active_storage()
        return storage.get_path()

    def _flush_to_disk(self, base_path):
        """
        Écrit le buffer dans le fichier CSV.
        """

        if not self.buffer:
            return

        file_path = os.path.join(base_path, self.session_filename)
        file_exists = os.path.exists(file_path)

        try:
            with open(file_path, mode="a", newline="") as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow(["timestamp", "temperature", "heating", "switch"])

                writer.writerows(self.buffer)

            print(f"{len(self.buffer)} lignes écrites dans : {file_path}")
            self.buffer.clear()

        except PermissionError:
            print(f"⚠ Accès refusé : {file_path}")
        except Exception as e:
            print(f"⚠ Erreur flush : {e}")

    def close(self):
        """
        Force l'écriture du buffer.
        """

        try:
            base_path = self._get_base_path()
            self._flush_to_disk(base_path)
        except Exception as e:
            print(f"⚠ LoggerService.close : {e}")

    def _generate_session_filename(self):
        """
        Génère un nom de fichier unique basé sur la date.
        """
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"temperature_{timestamp_str}.csv"
