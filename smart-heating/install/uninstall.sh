#!/bin/bash

set -e

echo "=== Désinstallation de Smart Heating ==="

INSTALL_DIR="/opt/smart-heating"
USER_NAME="smartheating"
SERVICE_NAME="smart-heating"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# ==========================
# === Étape 1 : arrêt service
# ==========================

echo "Arrêt du service..."

sudo systemctl stop $SERVICE_NAME || true

# ==========================
# === Étape 2 : désactivation
# ==========================

echo "Désactivation du service..."

sudo systemctl disable $SERVICE_NAME || true

# ==========================
# === Étape 3 : suppression service
# ==========================

echo "Suppression du service systemd..."

sudo rm -f $SERVICE_FILE

# Reload systemd
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# ==========================
# === Étape 4 : suppression fichiers
# ==========================

echo "Suppression du dossier projet..."

sudo rm -rf $INSTALL_DIR

# ==========================
# === Étape 5 : suppression utilisateur
# ==========================

echo "Suppression utilisateur $USER_NAME..."

if id "$USER_NAME" &>/dev/null; then
    sudo userdel -r $USER_NAME || true
    echo "Utilisateur supprimé."
else
    echo "Utilisateur inexistant."
fi

# ==========================
# === FIN
# ==========================

echo ""
echo "=== Désinstallation terminée ==="
