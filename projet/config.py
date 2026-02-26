"""
config.py

Configuration centrale du projet Smart Heating.
Adapté au Raspberry Pi 3.
"""

# ==========================
# === SYSTEME
# ==========================

RASPBERRY_MODEL = "Raspberry Pi 3"
PYTHON_VERSION = "3.13.5"

# ==========================
# === SONDE DS18B20
# ==========================

ONE_WIRE_GPIO = 4
SENSOR_ID = "28-c3f1cb0664ff"
W1_BASE_PATH = "/sys/bus/w1/devices/"

# ==========================
# === GPIO
# ==========================

LED_GPIO = 17
SWITCH_GPIO = 27

# ==========================
# === TEMPERATURE
# ==========================

TEMPERATURE_TARGET = 22.0
TEMPERATURE_TOLERANCE = 0.5

# ==========================
# === STOCKAGE
# ==========================

# Point de montage USB
USB_MOUNT_PATH = "/mnt/usb_backup"

# Systèmes de fichiers supportés
SUPPORTED_USB_FILESYSTEMS = ["vfat", "ntfs"]

# Dossier fallback local
LOCAL_STORAGE_PATH = "logs"

# ==========================
# === APPLICATION
# ==========================

DEBUG_MODE = True
LOG_INTERVAL_SECONDS = 10

# ==========================
# === CSV
# ==========================

CSV_FILENAME_PREFIX = "temperature"
CSV_DATE_FORMAT = "%Y-%m-%d"
CSV_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"