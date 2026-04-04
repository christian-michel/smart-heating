#!/bin/bash

set -e

echo "Installation de Smart Heating..."

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="/opt/smart-heating"

echo "Source : $PROJECT_ROOT"
echo "Installation dans : $INSTALL_DIR"

# --- Étape 0 : copie projet ---
echo "Copie du projet..."

sudo rm -rf $INSTALL_DIR
sudo mkdir -p $INSTALL_DIR

sudo cp -r $PROJECT_ROOT/* $INSTALL_DIR

# Permissions
sudo chown -R $USER:$USER $INSTALL_DIR

# --- Étape 1 : dépendances système ---
echo "Étape 1 : dépendances système"
cd $INSTALL_DIR/install
sudo ./setup_dependencies.sh

# --- Étape 2 : environnement Python ---
echo "Étape 2 : création environnement Python"

cd $INSTALL_DIR

if [ -d "backend/.venv" ]; then
    rm -rf backend/.venv
fi

python3 -m venv backend/.venv

source backend/.venv/bin/activate
pip install --upgrade pip

# --- Étape 3 : dépendances Python ---
echo "Étape 3 : installation dépendances Python"

pip install -r requirements.txt

# --- Étape 4 : test ---
echo "Test..."

python -c "import gpiozero, gpiod; print('✅ GPIO OK')"

echo ""
echo "Installation terminée dans $INSTALL_DIR"