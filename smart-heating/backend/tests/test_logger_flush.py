"""
test_logger_flush.py

Test de LoggerService avec flush automatique toutes les 60 secondes.
Simule l'écriture de données toutes les 5 secondes pendant 2 minutes.
"""

import time
from services.logger_service import LoggerService

# --- Initialisation du logger ---
logger = LoggerService()

# --- Paramètres du test ---
test_duration = 120 # durée totale du test en secondes (2 minutes)
log_interval = 5 # intervalle entre chaque log en secondes
start_time = time.time()

print("Début du test LoggerService avec flush automatique...")

while time.time() - start_time < test_duration:
    # Simuler une température aléatoire
    temperature = 20 + (time.time() % 5) # juste un chiffre qui varie pour le test
    heating_state = True
    switch_state = False

    # Écriture dans le logger
    logger.log(temperature, heating_state, switch_state)

    # Attente avant le prochain log
    time.sleep(log_interval)

print("Test terminé. Vérifie le fichier CSV dans le répertoire de stockage.")
