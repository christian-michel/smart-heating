#!/bin/bash

# ==========================
# === CONFIG
# ==========================

INSTALL_DIR="/opt/smart-heating"
VENV_PATH="$INSTALL_DIR/venv"
MAIN_MODULE="backend.core.thermostat"
USER_NAME="smartheating"

# ==========================
# === SÉCURITÉ
# ==========================

if [ ! -d "$INSTALL_DIR" ]; then
	echo "❌ Dossier $INSTALL_DIR introuvable"
	exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
	echo "❌ Environnement virtuel introuvable"
	exit 1
fi

# Chargement variables d'environnement
if [ -f "$INSTALL_DIR/.env" ]; then
	export $(grep -v '^#' $INSTALL_DIR/.env | xargs)
fi

# ==========================
# === LANCEMENT
# ==========================

echo "=== Smart Heating (manual run) ==="
echo "User : $USER_NAME"
echo "Directory : $INSTALL_DIR"
echo ""

# Toujours exécuter comme smartheating
sudo -u $USER_NAME -H bash -c "
cd $INSTALL_DIR

# Activation venv
source $VENV_PATH/bin/activate

# Fix GPIO (important)
export GPIOZERO_PIN_FACTORY=lgpio

# Lancement thermostat
python -m $MAIN_MODULE
"
