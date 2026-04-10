"""
thermostat.py

Responsabilité :
- Piloter le chauffage en fonction de la température
- Gérer le mode manuel via bouton GPIO
- Logger les données
- Assurer un arrêt propre du système

Robustesse :
- Compatible sans GPIO (mode simulation)
- Correction problème pin_factory (gpiozero)
- Protection contre concurrence (threading.Lock)
"""

import time
import threading

# ==========================
# === GPIO CONFIGURATION (FIX CRITIQUE)
# ==========================

try:
    from gpiozero import Device
    from gpiozero.pins.lgpio import LGPIOFactory

    Device.pin_factory = LGPIOFactory()
    print("[Thermostat] Pin factory forcée : LGPIO")

    from gpiozero import Button
    GPIO_AVAILABLE = True

except Exception as e:
    print(f"[Thermostat] GPIO indisponible → mode simulation : {e}")
    GPIO_AVAILABLE = False
    Button = None

# ==========================
# === IMPORTS BACKEND
# ==========================

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
    """
    Thermostat principal.

    Gère :
    - température
    - chauffage
    - bouton
    - logging
    """

    def __init__(self):
        # Stabilisation système (boot Raspberry)
        time.sleep(1)

        self.sensor = TemperatureSensor()
        self.heating = HeatingSystem()
        self.logger = LoggerService()

        self.last_log_time = 0
        self.manual_mode = False

        # 🔒 Protection concurrence
        self.lock = threading.Lock()

        # ==========================
        # === BOUTON GPIO
        # ==========================
        self.button = None

        if GPIO_AVAILABLE:
            try:
                self.button = Button(SWITCH_GPIO, pull_up=True)
                self.button.when_pressed = self.toggle_mode
                print(f"[Thermostat] Bouton GPIO actif (pin={SWITCH_GPIO})")
            except Exception as e:
                print(f"[Thermostat] Erreur bouton → désactivé : {e}")
        else:
            print("[Thermostat] Mode simulation → pas de bouton")

    # ==========================
    # === CALLBACK BOUTON
    # ==========================

    def toggle_mode(self):
        """
        Callback bouton (thread gpiozero)
        """
        with self.lock:
            self.manual_mode = not self.manual_mode
            print("\n>>> TOGGLE chauffage :", "ON" if self.manual_mode else "AUTO")

    # ==========================
    # === BOUCLE PRINCIPALE
    # ==========================

    def update(self):
        try:
            with self.lock:
                temperature = self.sensor.get_temperature()

                print(f"Température : {temperature} °C")
                print(f"Mode : {'MANUEL (FORCÉ ON)' if self.manual_mode else 'AUTO'}")

                # ==========================
                # === LOGIQUE CHAUFFAGE
                # ==========================

                # 🔥 MODE MANUEL PRIORITAIRE
                if self.manual_mode:
                    self.heating.turn_on()

                # 🤖 MODE AUTOMATIQUE
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
                        print("Température invalide → OFF sécurité")
                        self.heating.turn_off()

            # ==========================
            # === LOGGING
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
            print("⚠ Erreur update():", e)
            self.heating.turn_off()

    # ==========================
    # === CLEANUP
    # ==========================

    def cleanup(self):
        print("Nettoyage thermostat...")

        try:
            self.heating.turn_off()
        except Exception:
            pass

        # Flush logger
        try:
            self.logger.close()
            print("Logger flush final exécuté.")
        except Exception as e:
            print(f"Erreur flush Logger : {e}")

        # Sync finale
        try:
            if self.logger.storage_manager:
                print("Flush global des stockages...")
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