"""
logger_service.py

Responsabilité :
Enregistrer les données du thermostat dans un fichier CSV.

Test autonome :
python3 -m services.logger_service
"""

import os
import csv
from datetime import datetime
from config import LOG_DIRECTORY


class LoggerService:
    """
    Service de journalisation des données.
    """

    def __init__(self):
        os.makedirs(LOG_DIRECTORY, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        self.file_path = os.path.join(LOG_DIRECTORY, f"log_{date_str}.csv")

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "temperature", "heating", "switch"])

    def log(self, temperature, heating_state, switch_state):
        """
        Écrit une ligne dans le fichier CSV.
        """
        try:
            with open(self.file_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    temperature,
                    heating_state,
                    switch_state
                ])
        except Exception as e:
            print(f"Erreur écriture log : {e}")


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    print("Test logger...")

    logger = LoggerService()

    logger.log(21.5, True, True)
    logger.log(22.1, False, True)
    logger.log(23.0, False, False)

    print("3 lignes écrites.")
