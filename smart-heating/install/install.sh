#!/bin/bash

set -e # stop si erreur

echo "Installation de Smart Heating..."

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Projet : $PROJECT_ROOT"

# --- Étape 1 : dépendances système ---
echo "Étape 1 : dépendances système"
cd "$PROJECT_ROOT/install"
sudo ./setup_dependencies.sh

# --- Étape 2 : environnement Python ---
echo "Étape 2 : création environnement Python"

cd "$PROJECT_ROOT"

if [ -d "backend/.venv" ]; then
    echo "⚠ Environnement existant détecté → suppression"
    rm -rf backend/.venv
fi

python3 -m venv backend/.venv

# Activation
source backend/.venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# --- Étape 3 : dépendances Python ---
echo "Étape 3 : installation dépendances Python"

pip install -r requirements.txt

# --- Étape 4 : test rapide ---
echo "Étape 4 : test rapide Python"

python -c "import gpiozero, gpiod; print('✅ GPIO OK')"

echo ""
echo "Installation terminée avec succès !"
echo ""
echo "👉 Pour lancer le projet :"
echo "source backend/.venv/bin/activate"
