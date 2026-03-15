"""
heating.py

Responsabilité :
Piloter la LED simulant le chauffage.

Implémentation basée sur gpiozero.
"""

from gpiozero import LED
from backend.config import LED_GPIO


class HeatingSystem:
    """
    Classe permettant de contrôler le chauffage (LED).
    """

    def __init__(self):
        self.led = LED(LED_GPIO)
        self.state = False

    def turn_on(self):
        self.led.on()
        self.state = True

    def turn_off(self):
        self.led.off()
        self.state = False


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":

    import time

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