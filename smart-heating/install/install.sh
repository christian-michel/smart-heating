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
pip install uvicorn fastapi
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
API_TOKEN=changeme
EOF
    echo "Fichier .env créé"
else
    echo ".env existant conservé"
fi

chown $USER_NAME:$USER_NAME $ENV_FILE
chmod 600 $ENV_FILE

# ==========================
# === USB MANAGEMENT (FIABLE)
# ==========================

echo "Configuration USB..."

# Nettoyage double montage
while mount | grep "$USB_MOUNT" > /dev/null; do
    umount $USB_MOUNT || break
done

# Détection USB fiable
USB_DEVICE=""

if [ -e "/dev/sda1" ]; then
    USB_DEVICE="/dev/sda1"
else
    USB_DEVICE=$(lsblk -rpno NAME,TRAN | grep usb | awk '{print $1}' | head -n 1)
fi

if [ -n "$USB_DEVICE" ]; then
    echo "USB détectée : $USB_DEVICE"

    if mount $USB_DEVICE $USB_MOUNT; then
        echo "✅ Montage OK"
    else
        echo "❌ Échec montage"
    fi
else
    echo "⚠ Aucun USB détecté"
fi

# Permissions EXT4
if mount | grep "$USB_MOUNT" > /dev/null; then
    chown -R $USER_NAME:$USER_NAME $USB_MOUNT
    chmod -R 755 $USB_MOUNT

    if sudo -u $USER_NAME touch $USB_MOUNT/test.txt 2>/dev/null; then
        echo "✅ Écriture OK"
        rm -f $USB_MOUNT/test.txt
    else
        echo "❌ Écriture KO"
    fi
fi

# ==========================
# === TEST PYTHON
# ==========================

echo "Test Python..."

sudo -u $USER_NAME $INSTALL_DIR/venv/bin/python -c "import gpiozero; print('GPIO OK')"

# ==========================
# === SYSTEMD (API MODE)
# ==========================

echo "Installation service systemd..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

cat > $SERVICE_FILE <<EOF
[Unit]
Description=Smart Heating API (FastAPI + Controller)
After=network.target

[Service]
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$INSTALL_DIR

ExecStart=$INSTALL_DIR/venv/bin/uvicorn backend.api.api_server:app --host 0.0.0.0 --port 8000

Restart=always
RestartSec=5

EnvironmentFile=$ENV_FILE
Environment=PYTHONUNBUFFERED=1
Environment=GPIOZERO_PIN_FACTORY=lgpio
Environment=PYTHONPATH=$INSTALL_DIR

StandardOutput=journal
StandardError=journal

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
    echo "✅ Service actif (API disponible)"
else
    echo "❌ Service en échec"
    journalctl -u $SERVICE_NAME -n 50
fi

# ==========================
# === FIN
# ==========================

echo ""
echo "======================================"
echo "✅ Installation terminée (MODE API)"
echo "======================================"

echo ""
echo "🌐 Accès API :"
echo "http://<IP_RASPBERRY>:8000/docs"

echo ""
echo "⚠ IMPORTANT :"
echo "- Modifier TOKEN : $ENV_FILE"
echo "- Vérifier USB : lsblk / mount"

echo ""
echo "Commandes utiles :"
echo " systemctl status $SERVICE_NAME"
echo " journalctl -u $SERVICE_NAME -f"
