#!/bin/bash

set -e

echo "=== Installation de Smart Heating ==="

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="/opt/smart-heating"
USER_NAME="smartheating"
SERVICE_NAME="smart-heating"

echo "Source : $PROJECT_ROOT"
echo "Installation dans : $INSTALL_DIR"

# ==========================
# === Étape 0 : utilisateur
# ==========================

echo "Création utilisateur $USER_NAME..."

if id "$USER_NAME" &>/dev/null; then
    echo "Utilisateur déjà existant."
else
    sudo useradd -m -s /bin/bash $USER_NAME
    echo "Utilisateur créé."
fi

# Groupes nécessaires GPIO
sudo usermod -aG gpio $USER_NAME
sudo usermod -aG dialout $USER_NAME

# ==========================
# === Étape 1 : structure
# ==========================

echo "Création structure projet..."

sudo rm -rf $INSTALL_DIR
sudo mkdir -p $INSTALL_DIR
sudo mkdir -p $INSTALL_DIR/data

# ==========================
# === Étape 2 : copie projet
# ==========================

echo "Copie du projet..."

sudo cp -r $PROJECT_ROOT/* $INSTALL_DIR

# ==========================
# === Étape 3 : permissions
# ==========================

echo "Configuration des permissions..."

sudo chown -R $USER_NAME:$USER_NAME $INSTALL_DIR
sudo chmod -R 755 $INSTALL_DIR

# ==========================
# === Étape 4 : dépendances système
# ==========================

echo "Installation dépendances système..."

cd $INSTALL_DIR/install
sudo ./setup_dependencies.sh

# ==========================
# === Étape 5 : environnement Python
# ==========================

echo "Création environnement Python..."

cd $INSTALL_DIR

# Nettoyage ancien venv
sudo rm -rf venv

# Création venv avec bon user
sudo -u $USER_NAME python3 -m venv venv

# Installation dépendances Python
sudo -u $USER_NAME bash -c "
source $INSTALL_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r $INSTALL_DIR/requirements.txt
"

# ==========================
# === Étape 6 : test Python
# ==========================

echo "Test environnement Python..."

sudo -u $USER_NAME $INSTALL_DIR/venv/bin/python -c "import gpiozero; print('✅ GPIO OK')"

# ==========================
# === Étape 7 : systemd
# ==========================

echo "Installation du service systemd..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
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

Environment=PYTHONUNBUFFERED=1
Environment=GPIOZERO_PIN_FACTORY=lgpio

[Install]
WantedBy=multi-user.target
EOF

# Recharge systemd
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Activation + démarrage
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service $SERVICE_NAME installé et démarré"

# ==========================
# === FIN
# ==========================

echo ""
echo "=== Installation terminée ==="
echo "Utilisateur : $USER_NAME"
echo "Dossier : $INSTALL_DIR"
echo ""
echo "Commandes utiles :"
echo " sudo systemctl status $SERVICE_NAME"
echo " journalctl -u $SERVICE_NAME -f"