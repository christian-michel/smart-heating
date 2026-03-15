"""
test_dropbox_storage.py

Script de test pour DropboxStorage.
Crée un CSV test, synchronise vers Dropbox, et vérifie la suppression locale.
"""

import os
import csv
from datetime import datetime
from backend.services.storage.dropbox_storage import DropboxStorage
from backend.services.storage.local_storage import LocalStorage

# --- Étape 1 : Préparer un fichier CSV test dans le storage local ---
local_storage = LocalStorage() # dossier 'data/' par défaut
test_filename = f"test_dropbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
test_filepath = os.path.join(local_storage.get_path(), test_filename)

# Crée un petit fichier CSV test
with open(test_filepath, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "temperature", "heating", "switch"])
    writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 22.5, True, False])

print(f"Fichier CSV test créé : {test_filepath}")

# --- Étape 2 : Initialiser DropboxStorage ---
dropbox = DropboxStorage()

# --- Étape 3 : Synchroniser vers Dropbox ---
dropbox.sync(local_storage)

# --- Étape 4 : Vérifier si le fichier a été supprimé localement après upload ---
if not os.path.exists(test_filepath):
    print(f"✅ Test réussi : le fichier {test_filename} a été uploadé et supprimé localement.")
else:
    print(f"⚠ Test échoué : le fichier {test_filename} existe encore localement.")