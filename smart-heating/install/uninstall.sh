#!/bin/bash

set -e

echo "======================================"
echo "=== Smart Heating Uninstaller (PRO) ==="
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

INSTALL_DIR="/opt/smart-heating"
USER_NAME="smartheating"
SERVICE_NAME="smart-heating"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USB_MOUNT="/mnt/usb_backup"

# ==========================
# === STOP SERVICE
# ==========================

echo "Arrêt du service..."

if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
    systemctl stop $SERVICE_NAME || true
    echo "Service arrêté"
else
    echo "Service non actif"
fi

# ==========================
# === DISABLE SERVICE
# ==========================

echo "Désactivation du service..."

systemctl disable $SERVICE_NAME 2>/dev/null || true

# ==========================
# === REMOVE SERVICE FILE
# ==========================

echo "Suppression du service systemd..."

if [ -f "$SERVICE_FILE" ]; then
    rm -f $SERVICE_FILE
    echo "Fichier service supprimé"
else
    echo "Fichier service déjà absent"
fi

systemctl daemon-reexec
systemctl daemon-reload

# ==========================
# === REMOVE INSTALL DIR
# ==========================

echo "Suppression du projet..."

if [ -d "$INSTALL_DIR" ]; then
    rm -rf $INSTALL_DIR
    echo "Dossier supprimé"
else
    echo "Dossier déjà absent"
fi

# ==========================
# === USER HANDLING (SAFE)
# ==========================

echo "Gestion utilisateur..."

if id "$USER_NAME" &>/dev/null; then
    echo "Utilisateur détecté"

    # Vérifie si connecté
    if pgrep -u "$USER_NAME" > /dev/null; then
        echo "⚠ Utilisateur actif → suppression ignorée"
        echo "👉 Déconnecter l'utilisateur puis relancer si besoin"
    else
        userdel -r $USER_NAME || true
        echo "Utilisateur supprimé"
    fi
else
    echo "Utilisateur inexistant"
fi

# ==========================
# === USB CLEAN (OPTIONAL)
# ==========================

echo "Nettoyage USB..."

if mount | grep "$USB_MOUNT" > /dev/null; then
    echo "USB montée → démontage"
    umount $USB_MOUNT || echo "⚠ Impossible de démonter"
else
    echo "USB non montée"
fi

# ==========================
# === FINAL CHECK
# ==========================

echo ""
echo "Vérification finale..."

if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    echo "⚠ Service encore présent"
else
    echo "✅ Service supprimé"
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "⚠ Dossier encore présent"
else
    echo "✅ Dossier supprimé"
fi

echo ""
echo "======================================"
echo "✅ Désinstallation terminée"
echo "======================================"

echo ""
echo "ℹ️ Remarques :"
echo "- Les données USB ne sont PAS supprimées"
echo "- Le point de montage $USB_MOUNT est conservé"
echo "- Le système est revenu à l'état initial"