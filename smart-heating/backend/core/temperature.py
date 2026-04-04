"""
temperature.py

Responsabilité :
Lire la sonde DS18B20 via le système 1-Wire.

Version robuste :
- tolère les erreurs capteur
- conserve la dernière valeur valide
- évite les crashs du thermostat

Test autonome :
python -m backend.core.temperature
"""

import os
import time
from backend.config import SENSOR_ID, W1_BASE_PATH, DEBUG_MODE


class TemperatureSensor:
    """
    Classe permettant de lire la température
    depuis une sonde DS18B20.

    Comportement :
    - lecture brute du capteur
    - validation CRC
    - fallback sur dernière valeur valide en cas d'erreur
    """

    def __init__(self):
        self.device_file = os.path.join(
            W1_BASE_PATH,
            SENSOR_ID,
            "w1_slave"
        )
        self.last_valid_temperature = None

    def _read_raw(self):
        """
        Lit le fichier brut de la sonde.
        """
        with open(self.device_file, "r") as f:
            return f.readlines()

    def get_temperature(self):
        """
        Retourne la température en °C.

        Stratégie :
        - si lecture OK → retourne nouvelle valeur
        - sinon → retourne dernière valeur valide
        - sinon → retourne None
        """
        try:
            lines = self._read_raw()

            # Vérification CRC
            if lines[0].strip()[-3:] != "YES":
                raise RuntimeError("CRC invalide")

            # Extraction température
            temp_pos = lines[1].find("t=")
            if temp_pos == -1:
                raise RuntimeError("Température introuvable")

            temp_string = lines[1][temp_pos + 2:]
            temperature_c = float(temp_string) / 1000.0
            temperature_c = round(temperature_c, 2)

            self.last_valid_temperature = temperature_c
            return temperature_c

        except Exception as e:
            if DEBUG_MODE:
                print(f"[TemperatureSensor] Erreur : {e}")

            if self.last_valid_temperature is not None:
                if DEBUG_MODE:
                    print("[TemperatureSensor] fallback dernière valeur valide")
                return self.last_valid_temperature

            return None


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    print("=== Test lecture DS18B20 (robuste) ===")

    sensor = TemperatureSensor()

    try:
        while True:
            temp = sensor.get_temperature()
            print(f"Température : {temp} °C")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")