"""
logger_service.py

Responsabilité :
Gestion de l'enregistrement des données du thermostat.

Règles métier :
- 1 fichier CSV par lancement
- Rotation automatique toutes les 24h
- Flush régulier (buffer RAM)
- Sync uniquement à la fermeture ou rotation

Objectif :
- Zéro perte de données
- Zéro duplication de fichiers
"""

import os
import csv
import time
from datetime import datetime, timedelta

from backend.services.storage_manager import StorageManager


class LoggerService:

    def __init__(self, base_path: str = None, enable_sync: bool = True):

        self.base_path_override = base_path
        self.enable_sync = enable_sync

        # StorageManager uniquement en PROD
        self.storage_manager = None
        if self.base_path_override is None:
            self.storage_manager = StorageManager()

        # ==========================
        # === SESSION FILE
        # ==========================

        self.session_start_time = datetime.now()
        self.session_filename = self._generate_session_filename()
        self.current_file_date = self.session_start_time.date()

        # ==========================
        # === BUFFER
        # ==========================

        self.buffer = []
        self.buffer_limit = 5
        self.flush_interval = 10
        self.last_flush_time = time.time()

        print(f"[Logger] Session démarrée → {self.session_filename}")

    # ==========================
    # === LOG PRINCIPAL
    # ==========================

    def log(self, temperature: float, heating_state: bool, switch_state: bool):
        try:
            base_path = self._get_base_path()
            os.makedirs(base_path, exist_ok=True)

            # 🔥 Vérifier rotation quotidienne
            self._check_daily_rotation(base_path)

            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                temperature,
                heating_state,
                switch_state
            ]

            self.buffer.append(row)

            current_time = time.time()
            time_since_last_flush = current_time - self.last_flush_time

            if (
                len(self.buffer) >= self.buffer_limit
                or time_since_last_flush >= self.flush_interval
            ):
                self._flush_to_disk(base_path)
                self.last_flush_time = current_time

        except Exception as e:
            print(f"⚠ LoggerService.log : erreur -> {e}")

    # ==========================
    # === ROTATION JOURNALIÈRE
    # ==========================

    def _check_daily_rotation(self, base_path: str):
        current_date = datetime.now().date()

        if current_date != self.current_file_date:
            print("[Logger] 🔄 Rotation quotidienne du fichier")

            # 1️⃣ Flush du fichier courant
            self._flush_to_disk(base_path)

            # 2️⃣ Sync finale
            if self.enable_sync and self.storage_manager:
                print("[Logger] Sync après rotation")
                self.storage_manager.flush_all()

            # 3️⃣ Nouveau fichier
            self.session_start_time = datetime.now()
            self.session_filename = self._generate_session_filename()
            self.current_file_date = current_date

            print(f"[Logger] Nouveau fichier → {self.session_filename}")

    # ==========================
    # === PATH
    # ==========================

    def _get_base_path(self) -> str:

        if self.base_path_override is not None:
            return self.base_path_override

        try:
            storage = self.storage_manager.get_active_storage()
            return storage.get_path()

        except Exception as e:
            print(f"[Logger] fallback local : {e}")
            return "/tmp"

    # ==========================
    # === FLUSH
    # ==========================

    def _flush_to_disk(self, base_path: str):

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

            print(f"[Logger] {len(self.buffer)} lignes écrites → {self.session_filename}")

            self.buffer.clear()

        except Exception as e:
            print(f"⚠ Logger flush error : {e}")

    # ==========================
    # === CLOSE (CRITIQUE)
    # ==========================

    def close(self):
        try:
            print("[Logger] Fermeture → flush final")

            base_path = self._get_base_path()

            # 1️⃣ Flush final
            self._flush_to_disk(base_path)

            # 2️⃣ Sync finale
            if self.enable_sync and self.storage_manager:
                print("[Logger] Sync finale")
                self.storage_manager.flush_all()

        except Exception as e:
            print(f"⚠ LoggerService.close : {e}")

    # ==========================
    # === UTIL
    # ==========================

    def _generate_session_filename(self):
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"temperature_{timestamp_str}.csv"
