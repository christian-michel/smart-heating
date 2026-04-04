"""
main.py

Point d'entrée principal du système Smart Heating.

Responsabilités :
- Démarrer le thermostat
- Gérer la boucle principale
- Gérer l'arrêt propre (CTRL+C, systemd, etc.)

IMPORTANT :
Ce fichier ne contient AUCUNE logique métier.
Toute la logique est dans thermostat.py.
"""

import time
import signal
import sys

from backend.core.thermostat import Thermostat


class SmartHeatingApp:
    """
    Application principale encapsulant le thermostat.
    Permet un arrêt propre et une gestion claire du cycle de vie.
    """

    def __init__(self):
        self.thermostat = Thermostat()
        self.running = True

        # Gestion des signaux système (important pour systemd)
        signal.signal(signal.SIGINT, self.stop) # CTRL+C
        signal.signal(signal.SIGTERM, self.stop) # arrêt système

    def run(self):
        """
        Boucle principale.
        """
        print("Smart Heating démarré")

        try:
            while self.running:
                self.thermostat.update()
                time.sleep(0.1)

        except Exception as e:
            print(f"❌ Erreur critique dans la boucle principale : {e}")
            self.stop()

        finally:
            self.cleanup()

    def stop(self, *args):
        """
        Demande d'arrêt propre.
        """
        print("\nArrêt demandé...")
        self.running = False

    def cleanup(self):
        """
        Nettoyage global de l'application.
        """
        print("Nettoyage en cours...")
        try:
            self.thermostat.cleanup()
        except Exception as e:
            print(f"Erreur cleanup : {e}")

        print("✅ Arrêt propre terminé")
        sys.exit(0)


# ==========================
# === POINT D'ENTRÉE
# ==========================

if __name__ == "__main__":
    app = SmartHeatingApp()
    app.run()
