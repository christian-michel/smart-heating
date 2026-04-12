"""
app_controller.py

Contrôleur central du système Smart Heating.

Version PRO :
- Thread-safe
- Compatible FastAPI
- Gestion propre du cycle de vie
- Accès externe sécurisé (API)
"""

import time
import threading
import signal
import sys

from backend.core.thermostat import Thermostat


class AppController:
    """
    Contrôleur principal du système Smart Heating.
    """

    def __init__(self):
        self.thermostat = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        print("[AppController] Initialisé")

    # ==========================
    # === START SYSTEM
    # ==========================
    def start(self):
        with self.lock:
            if self.running:
                print("[AppController] Déjà en cours")
                return

            print("[AppController] Démarrage...")

            self.thermostat = Thermostat()
            self.running = True

            self.thread = threading.Thread(
                target=self._run_loop,
                daemon=True
            )
            self.thread.start()

            print("[AppController] Démarré")

    # ==========================
    # === MAIN LOOP
    # ==========================
    def _run_loop(self):
        try:
            while self.running:
                try:
                    if self.thermostat:
                        self.thermostat.update()
                except Exception as e:
                    print(f"[AppController] Erreur update : {e}")

                time.sleep(0.2)

        except Exception as e:
            print(f"[AppController] Erreur boucle : {e}")
            self.stop()

    # ==========================
    # === STOP SYSTEM
    # ==========================
    def stop(self):
        with self.lock:
            if not self.running:
                return

            print("[AppController] Arrêt...")

            self.running = False

            try:
                if self.thermostat:
                    self.thermostat.cleanup()
            except Exception as e:
                print(f"[AppController] Erreur cleanup : {e}")

            self.thermostat = None

            print("[AppController] Arrêt OK")

    # ==========================
    # === RESTART
    # ==========================
    def restart(self):
        print("[AppController] Restart demandé")
        self.stop()
        time.sleep(1)
        self.start()

    # ==========================
    # === STATUS (API READY)
    # ==========================
    def get_status(self):
        with self.lock:
            if not self.thermostat:
                return {
                    "running": False,
                    "temperature": None,
                    "heating": False,
                    "manual_mode": False
                }

            try:
                temperature = self.thermostat.sensor.get_temperature()
            except Exception:
                temperature = None

            return {
                "running": self.running,
                "temperature": temperature,
                "heating": self.thermostat.heating.state,
                "manual_mode": self.thermostat.manual_mode
            }

    # ==========================
    # === API CONTROL METHODS
    # ==========================
    def set_manual_mode(self, enabled: bool):
        with self.lock:
            if not self.thermostat:
                return False

            print(f"[AppController] Mode manuel → {enabled}")
            self.thermostat.manual_mode = enabled
            return True

    def force_heating(self, enabled: bool):
        with self.lock:
            if not self.thermostat:
                return False

            print(f"[AppController] Chauffage forcé → {enabled}")

            try:
                if enabled:
                    self.thermostat.heating.turn_on()
                else:
                    self.thermostat.heating.turn_off()
                return True
            except Exception as e:
                print(f"[AppController] Erreur chauffage : {e}")
                return False

    # ==========================
    # === CLEANUP GLOBAL
    # ==========================
    def cleanup(self):
        print("[AppController] Cleanup global")
        self.stop()

    # ==========================
    # === SIGNAL HANDLING
    # ==========================
    def register_signals(self):
        def handler(sig, frame):
            print(f"[AppController] Signal reçu : {sig}")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)


# ==========================
# === ENTRYPOINT
# ==========================
if __name__ == "__main__":

    controller = AppController()
    controller.register_signals()
    controller.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        controller.cleanup()
