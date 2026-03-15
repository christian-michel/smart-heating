"""
logger_service.py

Gestion de l'enregistrement des données du thermostat
avec vérification dynamique du stockage.

Optimisation :
- Utilisation d'un buffer RAM pour réduire les écritures sur la carte SD.
- Flush automatique toutes les 60 secondes si des données restent en mémoire.
- Création automatique des dossiers si inexistants.
"""

import os
import csv
import time
from datetime import datetime

from backend.services.storage_manager import StorageManager


class LoggerService:

    def __init__(self):
        self.storage_manager = StorageManager()
        self.session_filename = self._generate_session_filename()

        # --- BUFFER RAM ---
        self.buffer = []

        # Nombre de lignes avant flush automatique
        self.buffer_limit = 10

        # Temps (en secondes) entre flush automatiques même si le buffer n'est pas plein
        self.flush_interval = 60 # 60 secondes

        # Timestamp du dernier flush (initialisé au démarrage)
        self.last_flush_time = time.time()

    def log(self, temperature: float, heating_state: bool, switch_state: bool):
        """
        Ajoute une ligne dans le buffer RAM.
        Déclenche un flush si le buffer est plein ou si flush_interval est dépassé.
        """

        try:
            # 1 Récupération du stockage actif
            storage = self.storage_manager.get_active_storage()
            base_path = storage.get_path()

            # Vérifie si le dossier existe, sinon le crée
            if not os.path.exists(base_path):
                os.makedirs(base_path, exist_ok=True)

            # 2 Création de la ligne de données
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                temperature,
                heating_state,
                switch_state
            ]

            # 3 Ajout de la ligne dans le buffer RAM
            self.buffer.append(row)

            current_time = time.time()
            time_since_last_flush = current_time - self.last_flush_time

            # 4 Flush si buffer plein ou intervalle dépassé
            if len(self.buffer) >= self.buffer_limit or time_since_last_flush >= self.flush_interval:

                self._flush_to_disk(base_path)

                # Mise à jour du timestamp après flush
                self.last_flush_time = current_time

                # Synchronisation après écriture
                self.storage_manager.refresh()

        except Exception as e:
            print(f"⚠ LoggerService.log : erreur pendant l'ajout de la ligne -> {e}")

    def _flush_to_disk(self, base_path):
        """
        Écrit toutes les lignes du buffer dans le fichier CSV
        puis vide le buffer.
        """

        if not self.buffer:
            return

        file_path = os.path.join(base_path, self.session_filename)
        file_exists = os.path.exists(file_path)

        try:
            with open(file_path, mode="a", newline="") as file:
                writer = csv.writer(file)

                # Si le fichier n'existe pas encore, on écrit l'entête
                if not file_exists:
                    writer.writerow(["timestamp", "temperature", "heating", "switch"])

                # Écriture de toutes les lignes du buffer
                writer.writerows(self.buffer)

            print(f"{len(self.buffer)} lignes écrites dans : {file_path}")

            # On vide le buffer après écriture
            self.buffer.clear()

        except PermissionError:
            print(f"⚠ LoggerService : accès refusé pour {file_path}. Vérifier les droits.")
        except Exception as e:
            print(f"⚠ LoggerService : erreur lors du flush -> {e}")

    def close(self):
        """
        Force l'écriture de toutes les lignes restantes dans le CSV.
        À appeler à l'arrêt du thermostat.
        """
        try:
            storage = self.storage_manager.get_active_storage()
            base_path = storage.get_path()
            self._flush_to_disk(base_path)
        except Exception as e:
            print(f"⚠ LoggerService.close : {e}")

    def _generate_session_filename(self):
        """
        Génère le nom de fichier CSV basé sur la date et l'heure.
        """
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"temperature_{timestamp_str}.csv"