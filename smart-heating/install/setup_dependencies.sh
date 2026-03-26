#!/bin/bash

set -e # stop si erreur

echo "Installation des dépendances système..."

# --- Vérification root ---
if [ "$EUID" -ne 0 ]; then
  echo "⚠ Ce script doit être exécuté avec sudo"
  exit 1
fi

# --- Mise à jour ---
echo "Mise à jour des paquets..."
apt update

# --- Installation outils essentiels ---
echo "Installation des outils de build..."

apt install -y \
    build-essential \
    python3-dev \
    python3-venv \
    python3-pip \
    swig \
    git \
    curl

# --- Installation dépendances projet ---
if [ -f ../dependencies_apt.txt ]; then
    echo "Installation des dépendances APT du projet..."
    xargs -a ../dependencies_apt.txt apt install -y
else
    echo "⚠ Fichier dependencies_apt.txt introuvable"
    exit 1
fi

echo "✅ Toutes les dépendances système sont installées"