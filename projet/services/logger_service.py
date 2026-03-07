"""
logger_service.py

Gestion de l'enregistrement des données du thermostat
avec vérification dynamique du stockage.
"""

import os
import csv
from datetime import datetime

from services.storage_manager import StorageManager


class LoggerService:

    def __init__(self):
        self.storage_manager = StorageManager()
        self.session_filename = self._generate_session_filename()

    def log(self, temperature: float, heating_state: bool, switch_state: bool):
        """
        Enregistre une ligne de données et déclenche les synchronisations.
        """

        # 1 Vérifie le stockage actif
        self.storage_manager.refresh()
        storage = self.storage_manager.get_active_storage()
        base_path = storage.get_path()

        file_path = os.path.join(base_path, self.session_filename)
        file_exists = os.path.exists(file_path)

        try:
            # 2 Écriture du CSV
            with open(file_path, mode="a", newline="") as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow(["timestamp", "temperature", "heating", "switch"])

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    temperature,
                    heating_state,
                    switch_state
                ])

            print(f"Données enregistrées dans : {file_path}")

        except Exception as e:
            print(f"Erreur LoggerService : {e}")
            return

        # 3 Synchronisation APRÈS écriture
        self.storage_manager.refresh()

    def _generate_session_filename(self):
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"temperature_{timestamp_str}.csv"