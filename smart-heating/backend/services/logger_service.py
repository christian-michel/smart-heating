"""
logger_service.py

Responsabilité :
Gestion de l'enregistrement des données du thermostat.

Philosophie :
- Fiabilité > performance (IoT critique)
- Aucun crash bloquant
- Données persistées rapidement

Fonctionnement :
- Buffer RAM (réduction écritures disque)
- Flush automatique (taille OU temps)
- Flush forcé à l'arrêt (critique)
"""

import os
import csv
import time
from datetime import datetime

from backend.services.storage_manager import StorageManager


class LoggerService:
    """
    Service de logging du thermostat.

    Gère :
    - buffer RAM
    - écriture CSV sur le stockage le plus fiable
    - synchronisation vers USB / Dropbox
    """

    def __init__(self, base_path: str = None, enable_sync: bool = True):
        self.base_path_override = base_path
        self.enable_sync = enable_sync

        # StorageManager uniquement en mode PROD
        self.storage_manager = None
        if self.base_path_override is None:
            self.storage_manager = StorageManager()

        # Nom du fichier pour la session
        self.session_filename = self._generate_session_filename()

        # ==========================
        # === BUFFER RAM
        # ==========================
        self.buffer = []
        self.buffer_limit = 5
        self.flush_interval = 10
        self.last_flush_time = time.time()

        print(f"[Logger] Initialisé | fichier = {self.session_filename}")

    # ==========================
    # === LOG PRINCIPAL
    # ==========================
    def log(self, temperature: float, heating_state: bool, switch_state: bool):
        try:
            base_path = self._get_base_path()
            os.makedirs(base_path, exist_ok=True)

            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                temperature,
                heating_state,
                switch_state
            ]
            self.buffer.append(row)

            print(f"[Logger] buffer size = {len(self.buffer)}")

            current_time = time.time()
            time_since_last_flush = current_time - self.last_flush_time
            should_flush = len(self.buffer) >= self.buffer_limit or time_since_last_flush >= self.flush_interval

            if should_flush:
                print("[Logger] condition de flush atteinte")
                self._flush_to_disk(base_path)
                self.last_flush_time = current_time
                if self.enable_sync and self.storage_manager:
                    print("[Logger] synchronisation StorageManager après flush")
                    self.storage_manager.refresh()

        except Exception as e:
            print(f"⚠ LoggerService.log : erreur -> {e}")

    # ==========================
    # === PATH
    # ==========================
    def _get_base_path(self) -> str:
        if self.base_path_override is not None:
            return self.base_path_override

        # Priorité USB, sinon local
        if self.storage_manager.usb_storage.is_available():
            path = self.storage_manager.usb_storage.get_path()
            print(f"[Logger] chemin actif (USB) = {path}")
            return path
        path = self.storage_manager.local_storage.get_path()
        print(f"[Logger] chemin actif (LOCAL) = {path}")
        return path

    # ==========================
    # === FLUSH DISQUE
    # ==========================
    def _flush_to_disk(self, base_path: str):
        if not self.buffer:
            print("[Logger] buffer vide, rien à écrire")
            return

        file_path = os.path.join(base_path, self.session_filename)
        file_exists = os.path.exists(file_path)

        try:
            print(f"[Logger] flush vers disque : {file_path}")
            with open(file_path, mode="a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["timestamp", "temperature", "heating", "switch"])
                writer.writerows(self.buffer)

            print(f"[Logger] {len(self.buffer)} lignes écrites")
            self.buffer.clear()

        except PermissionError:
            print(f"⚠ Accès refusé : {file_path}")
        except Exception as e:
            print(f"⚠ Erreur flush : {e}")

    # ==========================
    # === CLOSE (FLUSH FINAL INTELLIGENT)
    # ==========================
    def close(self):
        """
        Flush final intelligent :
        1. Écrit sur USB si disponible
        2. Sinon sur local
        3. Puis synchronisation finale Dropbox si activée
        """
        try:
            print("[Logger] fermeture → flush final")

            # 1️⃣ Choix stockage pour écriture
            if self.storage_manager and self.storage_manager.usb_storage.is_available():
                final_path = self.storage_manager.usb_storage.get_path()
            else:
                final_path = self.storage_manager.local_storage.get_path() if self.storage_manager else self.base_path_override

            self._flush_to_disk(final_path)

            # 2️⃣ Sync finale Dropbox si activée
            if self.enable_sync and self.storage_manager:
                print("[Logger] flush global des stockages...")
                self.storage_manager.refresh()
                print("Synchronisation finale effectuée.")

        except Exception as e:
            print(f"⚠ LoggerService.close : erreur → {e}")

    # ==========================
    # === UTIL
    # ==========================
    def _generate_session_filename(self):
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"temperature_{timestamp_str}.csv"
