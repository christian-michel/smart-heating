#!/bin/bash

PROJECT_DIR=~/domotique/temperature/smart-heating

echo "Nettoyage des caches Python..."

find $PROJECT_DIR -name "__pycache__" -type d -print -exec rm -r {} +
find $PROJECT_DIR -name "*.pyc" -print -delete

echo "✅ Nettoyage terminé"
