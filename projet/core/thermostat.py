"""
thermostat.py

Version sécurisée minimale :
- try/except autour de update()
- fail-safe chauffage
- bouton toggle + logique température inchangés
"""

import time
import RPi.GPIO as GPIO

from config import (
    TEMPERATURE_TARGET,
    TEMPERATURE_TOLERANCE,
    LOG_INTERVAL_SECONDS,
    SWITCH_GPIO
)

from core.temperature import TemperatureSensor
from core.heating import HeatingSystem
from services.logger_service import LoggerService


class Thermostat:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.sensor = TemperatureSensor()
        self.heating = HeatingSystem()
        self.logger = LoggerService()

        self.last_log_time = 0
        self.manual_mode = False

        # Setup bouton
        GPIO.setup(SWITCH_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Détection d'appui (front descendant)
        GPIO.add_event_detect(
            SWITCH_GPIO,
            GPIO.FALLING,
            callback=self.toggle_mode,
            bouncetime=200
        )

    def toggle_mode(self, channel):
        self.manual_mode = not self.manual_mode
        print("\n>>> TOGGLE chauffage :", "ON" if self.manual_mode else "OFF")

    def update(self):
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
        print("Nettoyage GPIO...")
        self.heating.turn_off()
        GPIO.cleanup()


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    print("Test thermostat sécurisé minimal...")

    thermostat = Thermostat()

    try:
        while True:
            thermostat.update()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        thermostat.cleanup()