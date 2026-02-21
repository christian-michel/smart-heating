"""
temperature.py

Responsabilité :
Lire la sonde DS18B20 via le système 1-Wire.

Test autonome :
python3 core/temperature.py
"""

import os
import time
from config import SENSOR_ID, W1_BASE_PATH, DEBUG_MODE


class TemperatureSensor:
    """
    Classe permettant de lire la température
    depuis une sonde DS18B20.
    """

    def __init__(self):
        self.device_file = os.path.join(
            W1_BASE_PATH,
            SENSOR_ID,
            "w1_slave"
        )

    def _read_raw(self):
        """
        Lit le fichier brut de la sonde.
        """
        try:
            with open(self.device_file, "r") as f:
                lines = f.readlines()
            return lines
        except FileNotFoundError:
            raise RuntimeError("Fichier sonde introuvable.")
        except Exception as e:
            raise RuntimeError(f"Erreur lecture sonde : {e}")

    def get_temperature(self):
        """
        Retourne la température en °C (float).
        Vérifie le CRC avant extraction.
        """
        lines = self._read_raw()

        # Vérification CRC
        if lines[0].strip()[-3:] != "YES":
            raise RuntimeError("CRC invalide. Lecture incorrecte.")

        # Extraction température
        temp_pos = lines[1].find("t=")
        if temp_pos == -1:
            raise RuntimeError("Température introuvable dans la lecture.")

        temp_string = lines[1][temp_pos + 2:]
        temperature_c = float(temp_string) / 1000.0

        return round(temperature_c, 2)


# ==========================
# === TEST AUTONOME
# ==========================

if __name__ == "__main__":
    print("Test lecture DS18B20...")

    sensor = TemperatureSensor()

    try:
        while True:
            temp = sensor.get_temperature()
            print(f"Température : {temp} °C")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    except Exception as e:
        print(f"Erreur : {e}")