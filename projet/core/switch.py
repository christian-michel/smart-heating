"""
switch.py

Responsabilité :
Lire l'état d'un interrupteur branché en pull-up.

Le GPIO est géré globalement par thermostat.py.
"""

import RPi.GPIO as GPIO
from config import SWITCH_GPIO


class Switch:
    """
    Classe permettant de lire l'état d'un interrupteur.
    """

    def __init__(self):
        GPIO.setup(SWITCH_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_on(self):
        """
        Retourne True si interrupteur activé.
        En pull-up :
        - 0 = appuyé / activé
        - 1 = relâché
        """
        return GPIO.input(SWITCH_GPIO) == GPIO.LOW


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    import time
    GPIO.setmode(GPIO.BCM)  # Seulement pour test autonome
    print("Test interrupteur (pull-up)...")

    switch = Switch()

    try:
        while True:
            if switch.is_on():
                print("Interrupteur : ON")
            else:
                print("Interrupteur : OFF")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        GPIO.cleanup()