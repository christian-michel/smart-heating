"""
thermostat.py

Responsabilité :
- Piloter le chauffage en fonction de la température
- Gérer le mode manuel via bouton GPIO
- Logger les données
- Assurer un arrêt propre du système

Améliorations :
- Protection contre les accès concurrents (threading.Lock)
- Gestion robuste des erreurs capteur (fallback)
- Correction bug bouton (race condition)
- Cleanup amélioré avec synchronisation finale
"""

import time
import threading
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
        # Stabilisation système (boot Raspberry)
        time.sleep(1)

        self.sensor = TemperatureSensor()
        self.heating = HeatingSystem()
        self.logger = LoggerService()

        self.last_log_time = 0
        self.manual_mode = False

        # 🔒 Protection contre concurrence (GPIO callback vs loop)
        self.lock = threading.Lock()

        # Bouton GPIO
        try:
            self.button = Button(SWITCH_GPIO, pull_up=True)
            self.button.when_pressed = self.toggle_mode
            print("Bouton GPIO initialisé (gpiozero).")
        except Exception as e:
            print("Impossible d'initialiser le bouton :", e)
            print("Le thermostat continue sans gestion du bouton.")

    def toggle_mode(self):
        """
        Callback bouton (thread gpiozero)
        → protégé par lock pour éviter race condition
        """
        with self.lock:
            self.manual_mode = not self.manual_mode
            print("\n>>> TOGGLE chauffage :", "ON" if self.manual_mode else "OFF")

    def update(self):
        """
        Boucle principale :
        - lecture température
        - contrôle chauffage
        - logging
        """
        try:
            with self.lock:
                temperature = self.sensor.get_temperature()

                print(f"Température : {temperature} °C")
                print(f"Mode manuel : {'ON' if self.manual_mode else 'OFF'}")

                # ==========================
                # Gestion chauffage
                # ==========================

                if not self.manual_mode:
                    # Mode OFF → sécurité
                    self.heating.turn_off()

                else:
                    if temperature is not None:
                        if (
                            not self.heating.state
                            and temperature < (TEMPERATURE_TARGET - TEMPERATURE_TOLERANCE)
                        ):
                            self.heating.turn_on()

                        elif (
                            self.heating.state
                            and temperature > (TEMPERATURE_TARGET + TEMPERATURE_TOLERANCE)
                        ):
                            self.heating.turn_off()

                    else:
                        print("Température invalide → chauffage OFF (sécurité)")
                        self.heating.turn_off()

            # ==========================
            # Logging (hors lock)
            # ==========================

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
        """
        Arrêt propre du système :
        - arrêt chauffage
        - flush des logs
        - synchronisation stockage (USB / Dropbox)
        """
        print("Nettoyage thermostat...")

        try:
            self.heating.turn_off()
        except Exception:
            pass

        # Flush Logger
        try:
            if hasattr(self.logger, 'buffer') and self.logger.buffer:
                active_storage = self.logger.storage_manager.get_active_storage()
                self.logger._flush_to_disk(active_storage.get_path())
                print("Logger flush final exécuté.")
        except Exception as e:
            print(f"Erreur flush Logger : {e}")

        # 🔥 Synchronisation finale (IMPORTANT)
        try:
            self.logger.storage_manager.flush_all()
            print("Synchronisation finale effectuée.")
        except Exception as e:
            print(f"Erreur synchronisation finale : {e}")


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    print("=== Test thermostat (version robuste) ===")

    thermostat = Thermostat()

    try:
        while True:
            thermostat.update()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")

    finally:
        thermostat.cleanup()