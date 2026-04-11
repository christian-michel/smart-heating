#!/bin/bash

set -e

echo "======================================"
echo "=== Smart Heating Installer (PRO) ===="
echo "======================================"

# ==========================
# === CHECK ROOT
# ==========================

if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté avec sudo"
    exit 1
fi

# ==========================
# === VARIABLES
# ==========================

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="/opt/smart-heating"
USER_NAME="smartheating"
SERVICE_NAME="smart-heating"
ENV_FILE="$INSTALL_DIR/.env"
USB_MOUNT="/mnt/usb_backup"

echo "Source : $PROJECT_ROOT"
echo "Installation dans : $INSTALL_DIR"

# ==========================
# === CLEAN PREVIOUS INSTALL
# ==========================

echo "Nettoyage ancienne installation..."

systemctl stop $SERVICE_NAME 2>/dev/null || true
systemctl disable $SERVICE_NAME 2>/dev/null || true
rm -f /etc/systemd/system/${SERVICE_NAME}.service

# ==========================
# === USER
# ==========================

echo "Création utilisateur..."

if id "$USER_NAME" &>/dev/null; then
    echo "Utilisateur déjà existant"
else
    useradd -m -s /bin/bash $USER_NAME
    echo "Utilisateur créé"
fi

usermod -aG gpio $USER_NAME
usermod -aG dialout $USER_NAME

# ==========================
# === STRUCTURE
# ==========================

echo "Création structure..."

rm -rf $INSTALL_DIR
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/data
mkdir -p $USB_MOUNT

# ==========================
# === COPY
# ==========================

echo "Copie du projet..."

cp -r $PROJECT_ROOT/* $INSTALL_DIR

chown -R $USER_NAME:$USER_NAME $INSTALL_DIR
chmod -R 755 $INSTALL_DIR

# ==========================
# === DEPENDENCIES
# ==========================

echo "Installation dépendances système..."

cd $INSTALL_DIR/install
./setup_dependencies.sh

# ==========================
# === PYTHON ENV
# ==========================

echo "Création environnement Python..."

cd $INSTALL_DIR

rm -rf venv

sudo -u $USER_NAME python3 -m venv venv

sudo -u $USER_NAME bash -c "
source $INSTALL_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r $INSTALL_DIR/requirements.txt
"

# ==========================
# === ENV FILE
# ==========================

echo "Configuration .env..."

if [ ! -f "$ENV_FILE" ]; then
cat > $ENV_FILE <<EOF
DROPBOX_APP_KEY=
DROPBOX_APP_SECRET=
DROPBOX_REFRESH_TOKEN=
EOF
    echo "Fichier .env créé"
else
    echo ".env existant conservé"
fi

chown $USER_NAME:$USER_NAME $ENV_FILE
chmod 600 $ENV_FILE

# ==========================
# === USB MANAGEMENT (FIX)
# ==========================

echo "Configuration USB..."

# 1️⃣ Nettoyage double montage
MOUNT_COUNT=$(mount | grep "$USB_MOUNT" | wc -l)

if [ "$MOUNT_COUNT" -gt 1 ]; then
    echo "⚠ Double montage détecté"
    while mount | grep "$USB_MOUNT" > /dev/null; do
        umount $USB_MOUNT || break
    done
fi

# 2️⃣ Détection device USB fiable
echo "Détection périphérique USB..."

USB_DEVICE=""

# Cas standard Raspberry
if [ -e "/dev/sda1" ]; then
    USB_DEVICE="/dev/sda1"
else
    # fallback intelligent
    USB_DEVICE=$(lsblk -rpno NAME,TYPE,TRAN | grep "part usb" | awk '{print $1}' | head -n 1)
fi

if [ -z "$USB_DEVICE" ]; then
    echo "❌ Aucun périphérique USB détecté"
else
    echo "USB détectée : $USB_DEVICE"
fi

# 3️⃣ Montage si nécessaire
if ! mount | grep "$USB_MOUNT" > /dev/null && [ -n "$USB_DEVICE" ]; then
    echo "Montage $USB_DEVICE → $USB_MOUNT"

    if mount $USB_DEVICE $USB_MOUNT; then
        echo "✅ Montage réussi"
    else
        echo "❌ Échec montage"
    fi
fi

# 4️⃣ Permissions EXT4
if mount | grep "$USB_MOUNT" > /dev/null; then
    echo "Configuration permissions..."

    chown -R $USER_NAME:$USER_NAME $USB_MOUNT
    chmod -R 755 $USB_MOUNT

    if sudo -u $USER_NAME touch $USB_MOUNT/test.txt 2>/dev/null; then
        echo "✅ Écriture OK"
        rm -f $USB_MOUNT/test.txt
    else
        echo "❌ Écriture KO"
    fi
else
    echo "⚠ USB non montée → fallback local"
fi

# ==========================
# === TEST PYTHON
# ==========================

echo "Test Python..."

sudo -u $USER_NAME $INSTALL_DIR/venv/bin/python -c "import gpiozero; print('GPIO OK')"

# ==========================
# === SYSTEMD
# ==========================

echo "Installation service..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

cat > $SERVICE_FILE <<EOF
[Unit]
Description=Smart Heating Thermostat
After=network.target

[Service]
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$INSTALL_DIR

ExecStart=$INSTALL_DIR/venv/bin/python -m backend.core.thermostat

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal

EnvironmentFile=$ENV_FILE
Environment=PYTHONUNBUFFERED=1
Environment=GPIOZERO_PIN_FACTORY=lgpio

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reexec
systemctl daemon-reload

systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# ==========================
# === VALIDATION
# ==========================

sleep 3

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service actif"
else
    echo "❌ Service en échec"
    journalctl -u $SERVICE_NAME -n 20
fi

# ==========================
# === FIN
# ==========================

echo ""
echo "======================================"
echo "✅ Installation terminée"
echo "======================================"

echo ""
echo "⚠ IMPORTANT :"
echo "- Vérifier la clé USB : lsblk"
echo "- Vérifier montage : mount | grep usb_backup"
echo "- Config Dropbox dans : $ENV_FILE"
