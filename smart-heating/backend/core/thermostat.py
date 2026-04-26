"""
thermostat.py
Version PRO+++ :
- Consigne dynamique (API)
- Hystérésis propre
- Anti court-cycle (protection matériel)
"""

import time
import threading

# ==========================
# === GPIO CONFIGURATION
# ==========================

try:
    from gpiozero import Device
    from gpiozero.pins.lgpio import LGPIOFactory

    Device.pin_factory = LGPIOFactory()
    print("[Thermostat] Pin factory forcée : LGPIO")

    from gpiozero import Button
    GPIO_AVAILABLE = True

except Exception as e:
    print(f"[Thermostat] GPIO indisponible → simulation : {e}")
    GPIO_AVAILABLE = False
    Button = None

# ==========================
# === IMPORTS
# ==========================

from backend.config import (
    TEMPERATURE_TOLERANCE,
    LOG_INTERVAL_SECONDS,
    SWITCH_GPIO
)

from backend.core.temperature import TemperatureSensor
from backend.core.heating import HeatingSystem
from backend.services.logger_service import LoggerService


class Thermostat:

    def __init__(self):
        time.sleep(1)

        self.sensor = TemperatureSensor()
        self.heating = HeatingSystem()
        self.logger = LoggerService()

        self.last_log_time = 0
        self.manual_mode = False

        # 🔥 Consigne dynamique (API)
        self.target_temperature = 19.0

        # 🔥 Anti court-cycle
        self.last_switch_time = 0
        self.min_cycle_time = 60 # secondes (à ajuster)

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
                print(f"[Thermostat] Bouton désactivé : {e}")
        else:
            print("[Thermostat] Mode simulation")

    # ==========================
    # === BOUTON
    # ==========================

    def toggle_mode(self):
        with self.lock:
            self.manual_mode = not self.manual_mode
            print(">>> MODE :", "MANUEL" if self.manual_mode else "AUTO")

    # ==========================
    # === ANTI COURT-CYCLE
    # ==========================

    def can_switch(self):
        """
        Vérifie si on peut changer l'état du chauffage
        """
        elapsed = time.time() - self.last_switch_time
        return elapsed >= self.min_cycle_time

    def record_switch(self):
        """
        Enregistre un changement d'état
        """
        self.last_switch_time = time.time()

    # ==========================
    # === RÉGULATION
    # ==========================

    def regulate(self, temperature):
        target = self.target_temperature
        tolerance = TEMPERATURE_TOLERANCE

        if temperature is None:
            print("Température invalide → OFF sécurité")
            self.heating.turn_off()
            return

        # 🔥 MODE MANUEL PRIORITAIRE
        if self.manual_mode:
            if not self.heating.state and self.can_switch():
                print("[Thermostat] MANUAL → ON")
                self.heating.turn_on()
                self.record_switch()
            return

        # 🤖 MODE AUTO
        if not self.heating.state:
            # Demande ON
            if temperature < (target - tolerance):
                if self.can_switch():
                    print(f"[Thermostat] ON (temp={temperature:.2f})")
                    self.heating.turn_on()
                    self.record_switch()
                else:
                    print("[Thermostat] ON bloqué (anti short-cycle)")

        else:
            # Demande OFF
            if temperature > (target + tolerance):
                if self.can_switch():
                    print(f"[Thermostat] OFF (temp={temperature:.2f})")
                    self.heating.turn_off()
                    self.record_switch()
                else:
                    print("[Thermostat] OFF bloqué (anti short-cycle)")

    # ==========================
    # === LOOP
    # ==========================

    def update(self):
        try:
            with self.lock:
                temperature = self.sensor.get_temperature()

                print(f"Température : {temperature} °C")
                print(f"Target : {self.target_temperature} °C")
                print(f"Mode : {'MANUEL' if self.manual_mode else 'AUTO'}")

                self.regulate(temperature)

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

        try:
            self.logger.close()
        except Exception:
            pass

        try:
            if self.logger.storage_manager:
                self.logger.storage_manager.flush_all()
        except Exception:
            pass


# ==========================
# === TEST
# ==========================

if __name__ == "__main__":
    thermostat = Thermostat()

    try:
        while True:
            thermostat.update()
            time.sleep(0.1)

    except KeyboardInterrupt:
        thermostat.cleanup()