"""
switch.py

Responsabilité :
Lire l'état d'un interrupteur branché en pull-up.

Implémentation basée sur gpiozero (backend lgpio recommandé).
"""

from gpiozero import Button
from backend.config import SWITCH_GPIO


class Switch:
    """
    Classe permettant de lire l'état d'un interrupteur.
    """

    def __init__(self):
        # pull_up=True correspond exactement à ton montage actuel
        self.button = Button(SWITCH_GPIO, pull_up=True)

    def is_on(self):
        """
        Retourne True si interrupteur activé.

        En pull-up :
        - appuyé = True
        - relâché = False
        """
        return self.button.is_pressed


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":

    import time

    print("Test interrupteur (gpiozero pull-up)...")

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