"""
app_controller.py

Contrôleur central Smart Heating

Version PRO++++ :
- State centralisé complet
- Thread-safe
- API-ready
- Sync bidirectionnelle Controller ↔ Thermostat
- Support consigne dynamique (target_temperature)
"""

import time
import threading
import signal
import sys

from backend.core.thermostat import Thermostat


class AppController:

    def __init__(self):
        self.thermostat = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # 🔥 STATE CENTRAL (source de vérité)
        self.state = {
            "running": False,
            "temperature": None,
            "heating": False,
            "manual_mode": False,
            "target_temperature": 19.0 # valeur par défaut
        }

        print("[AppController] Initialisé")

    # ==========================
    # === START
    # ==========================
    def start(self):
        with self.lock:
            if self.running:
                print("[AppController] Déjà en cours")
                return

            print("[AppController] Démarrage...")

            self.thermostat = Thermostat()

            # 🔥 Injection consigne initiale
            self.thermostat.target_temperature = self.state["target_temperature"]

            self.running = True
            self.state["running"] = True

            self.thread = threading.Thread(
                target=self._run_loop,
                daemon=True
            )
            self.thread.start()

            print("[AppController] Démarré")

    # ==========================
    # === LOOP
    # ==========================
    def _run_loop(self):
        try:
            while self.running:
                try:
                    if self.thermostat:
                        # 🔥 sync Controller → Thermostat (IMPORTANT)
                        self.thermostat.target_temperature = self.state.get(
                            "target_temperature", 19.0
                        )

                        self.thermostat.update()
                        self._sync_state()

                except Exception as e:
                    print(f"[AppController] Erreur update : {e}")

                time.sleep(0.2)

        except Exception as e:
            print(f"[AppController] Erreur boucle : {e}")
            self.stop()

    # ==========================
    # === SYNC STATE (Thermostat → Controller)
    # ==========================
    def _sync_state(self):
        try:
            temperature = self.thermostat.sensor.get_temperature()
        except Exception:
            temperature = None

        try:
            heating = self.thermostat.heating.state
        except Exception:
            heating = False

        try:
            manual_mode = self.thermostat.manual_mode
        except Exception:
            manual_mode = False

        try:
            target_temperature = self.thermostat.target_temperature
        except Exception:
            target_temperature = self.state["target_temperature"]

        self.state.update({
            "temperature": temperature,
            "heating": heating,
            "manual_mode": manual_mode,
            "target_temperature": target_temperature
        })

    # ==========================
    # === STOP
    # ==========================
    def stop(self):
        with self.lock:
            if not self.running:
                return

            print("[AppController] Arrêt...")

            self.running = False
            self.state["running"] = False

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
    # === STATUS
    # ==========================
    def get_status(self):
        with self.lock:
            return dict(self.state)

    # ==========================
    # === CONTROL API
    # ==========================
    def set_manual_mode(self, enabled: bool):
        with self.lock:
            if not self.thermostat:
                return False

            print(f"[AppController] Mode manuel → {enabled}")

            self.thermostat.manual_mode = enabled
            self.state["manual_mode"] = enabled

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

                self.state["heating"] = enabled
                return True

            except Exception as e:
                print(f"[AppController] Erreur chauffage : {e}")
                return False

    # ==========================
    # === TARGET TEMPERATURE API
    # ==========================
    def set_target_temperature(self, value: float):
        with self.lock:
            print(f"[AppController] Nouvelle consigne → {value}°C")

            try:
                self.state["target_temperature"] = value

                # 🔥 mise à jour immédiate thermostat
                if self.thermostat:
                    self.thermostat.target_temperature = value

                return True

            except Exception as e:
                print(f"[AppController] Erreur consigne : {e}")
                return False

    def get_target_temperature(self):
        return self.state.get("target_temperature", 19.0)

    # ==========================
    # === CLEANUP
    # ==========================
    def cleanup(self):
        print("[AppController] Cleanup global")
        self.stop()

    # ==========================
    # === SIGNALS
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
