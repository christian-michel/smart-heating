"""
heating.py

Responsabilité :
Piloter le système de chauffage via une LED (GPIO).

Philosophie :
- Une seule responsabilité : ON / OFF chauffage
- Aucun couplage avec stockage, thermostat ou logique métier
- Robuste face aux erreurs GPIO
- Compatible environnement sans GPIO (dev / Docker)

Comportement :
- Si GPIO disponible → contrôle réel de la LED
- Sinon → mode simulation (logs uniquement)

IMPORTANT :
Ce module ne doit JAMAIS :
- gérer la logique thermostat
- écrire dans des fichiers
- gérer Dropbox ou USB
"""

from backend.config import LED_GPIO

# ==========================
# === INIT GPIO ROBUSTE
# ==========================

GPIO_AVAILABLE = False

try:
    from gpiozero import LED, Device
    from gpiozero.pins.lgpio import LGPIOFactory

    # 🔥 Force le backend GPIO (CRITIQUE pour user non-root)
    Device.pin_factory = LGPIOFactory()

    GPIO_AVAILABLE = True

except Exception as e:
    print(f"[HeatingSystem] GPIO non disponible → mode simulation : {e}")
    GPIO_AVAILABLE = False


# ==========================
# === CLASSE PRINCIPALE
# ==========================

class HeatingSystem:
    """
    Classe permettant de contrôler le chauffage.

    Attributs :
    - state : état logique du chauffage (True = ON, False = OFF)
    - simulation_mode : True si GPIO indisponible
    """

    def __init__(self):
        self.state = False
        self.simulation_mode = False
        self.led = None

        if GPIO_AVAILABLE:
            try:
                self.led = LED(LED_GPIO)
                print(f"[HeatingSystem] GPIO actif (pin={LED_GPIO})")

            except Exception as e:
                print(f"[HeatingSystem] Erreur init GPIO → simulation : {e}")
                self.simulation_mode = True
        else:
            print("[HeatingSystem] Mode simulation activé")
            self.simulation_mode = True

    # ==========================
    # === ON / OFF
    # ==========================

    def turn_on(self):
        """
        Active le chauffage.
        """
        if self.state:
            return # évite appels inutiles

        if not self.simulation_mode and self.led:
            try:
                self.led.on()
                print("[HeatingSystem] Chauffage ON")

            except Exception as e:
                print(f"[HeatingSystem] Erreur GPIO turn_on : {e}")

        else:
            print("[HeatingSystem] (simulation) chauffage ON")

        self.state = True

    def turn_off(self):
        """
        Désactive le chauffage.
        """
        if not self.state:
            return # évite appels inutiles

        if not self.simulation_mode and self.led:
            try:
                self.led.off()
                print("[HeatingSystem] Chauffage OFF")

            except Exception as e:
                print(f"[HeatingSystem] Erreur GPIO turn_off : {e}")

        else:
            print("[HeatingSystem] (simulation) chauffage OFF")

        self.state = False

    # ==========================
    # === UTILS
    # ==========================

    def is_on(self) -> bool:
        """
        Retourne l'état actuel du chauffage.
        Utile pour les tests et le debug.
        """
        return self.state


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":

    import time

    print("=== Test système chauffage ===")

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
        print("Chauffage arrêté proprement.")
