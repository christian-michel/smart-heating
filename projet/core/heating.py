"""
heating.py

Responsabilité :
Piloter la LED simulant le chauffage.

Le GPIO est géré globalement par thermostat.py.
"""

import RPi.GPIO as GPIO
from config import LED_GPIO


class HeatingSystem:
    """
    Classe permettant de contrôler le chauffage (LED).
    """

    def __init__(self):
        GPIO.setup(LED_GPIO, GPIO.OUT)
        self.state = False

    def turn_on(self):
        GPIO.output(LED_GPIO, GPIO.HIGH)
        self.state = True

    def turn_off(self):
        GPIO.output(LED_GPIO, GPIO.LOW)
        self.state = False


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    import time
    GPIO.setmode(GPIO.BCM)  # Seulement pour test autonome
    print("Test système chauffage (LED)...")

    heating = HeatingSystem()

    try:
        while True:
            print("Chauffage ON")
            heating.turn_on()
            time.sleep(3)

            print("Chauffage OFF")
            heating.turn_off()
            time.sleep(3)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        heating.turn_off()
        GPIO.cleanup()