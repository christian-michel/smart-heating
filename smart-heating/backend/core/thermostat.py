"""
thermostat.py

Version sécurisée minimale (gpiozero) :
- try/except autour de update()
- fail-safe chauffage
- bouton toggle + logique température inchangés
- gestion bouton via gpiozero
- flush LoggerService à l'arrêt
- suppression du flush forcé après chaque log
"""

import time
from gpiozero import Button

# Import depuis le package backend
from backend.config import (
    TEMPERATURE_TARGET,
    TEMPERATURE_TOLERANCE,
    LOG_INTERVAL_SECONDS,
    SWITCH_GPIO
)

from backend.core.temperature import TemperatureSensor
from backend.core.heating import HeatingSystem
from backend.services.logger_service import LoggerService


class Thermostat:

    def __init__(self):
        # Pause initiale pour stabiliser le système
        time.sleep(1)

        self.sensor = TemperatureSensor()
        self.heating = HeatingSystem()
        self.logger = LoggerService()

        self.last_log_time = 0
        self.manual_mode = False

        # Bouton GPIO via gpiozero
        try:
            self.button = Button(SWITCH_GPIO, pull_up=True)
            self.button.when_pressed = self.toggle_mode
            print("Bouton GPIO initialisé (gpiozero).")
        except Exception as e:
            print("Impossible d'initialiser le bouton :", e)
            print("Le thermostat continue sans gestion du bouton.")

    def toggle_mode(self):
        """Change l'état manuel du chauffage"""
        self.manual_mode = not self.manual_mode
        print("\n>>> TOGGLE chauffage :", "ON" if self.manual_mode else "OFF")

    def update(self):
        """Lecture température et contrôle chauffage + logging"""
        try:
            temperature = self.sensor.get_temperature()
            print(f"Température : {temperature} °C")
            print(f"Mode manuel : {'ON' if self.manual_mode else 'OFF'}")

            # Gestion chauffage
            if not self.manual_mode:
                self.heating.turn_off()
            else:
                if temperature is not None:
                    if not self.heating.state and temperature < (TEMPERATURE_TARGET - TEMPERATURE_TOLERANCE):
                        self.heating.turn_on()
                    elif self.heating.state and temperature > (TEMPERATURE_TARGET + TEMPERATURE_TOLERANCE):
                        self.heating.turn_off()
                else:
                    print("Température invalide ! Chauffage OFF par sécurité.")
                    self.heating.turn_off()

            # Logging périodique
            current_time = time.time()
            if current_time - self.last_log_time >= LOG_INTERVAL_SECONDS:
                self.logger.log(
                    temperature,
                    self.heating.state,
                    self.manual_mode
                )
                self.last_log_time = current_time
                print("Donnée enregistrée.")

            print("-" * 30)

        except Exception as e:
            print("⚠ Erreur dans update():", e)
            print("Chauffage OFF par sécurité !")
            self.heating.turn_off()

    def cleanup(self):
        """Arrêt du chauffage et flush des données Logger"""
        print("Nettoyage thermostat...")
        try:
            self.heating.turn_off()
        except Exception:
            pass

        # Flush final du buffer Logger
        try:
            if hasattr(self.logger, 'buffer') and self.logger.buffer:
                active_storage = self.logger.storage_manager.get_active_storage()
                self.logger._flush_to_disk(active_storage.get_path())
                print("Logger flush final exécuté.")
        except Exception as e:
            print(f"Erreur lors du flush final du Logger : {e}")


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    print("Test thermostat sécurisé minimal (gpiozero)...")
    thermostat = Thermostat()

    try:
        while True:
            thermostat.update()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")

    finally:
        thermostat.cleanup()