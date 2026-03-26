"""
test_local_storage.py

Test complet pour backend.services.storage.local_storage.LocalStorage
- Vérifie la création du dossier de stockage
- Vérifie la synchronisation vers un stockage cible simulé (USB)
- Vérifie la suppression du fichier local après copie
"""

import os
import tempfile
from backend.services.storage.local_storage import LocalStorage

# --- 1️⃣ Création de LocalStorage ---
print("=== Initialisation de LocalStorage ===")
local_storage = LocalStorage()

base_path = local_storage.get_path()
print(f"Dossier local : {base_path}")
assert os.path.exists(base_path), "❌ Le dossier local n'a pas été créé !"
print("✅ Dossier local créé correctement.\n")

# --- 2️⃣ Création d'un fichier CSV test ---
csv_test_file = os.path.join(base_path, "test.csv")
with open(csv_test_file, "w", newline="") as f:
    f.write("timestamp,temperature,heating,switch\n")
    f.write("2026-03-15 10:00:00,20.5,True,False\n")
print(f"✅ Fichier CSV de test créé : {csv_test_file}\n")

# --- 3️⃣ Création d'un stockage USB simulé ---
usb_dir = tempfile.mkdtemp()
print(f"Dossier USB simulé : {usb_dir}\n")

# Classe simple simulant le stockage USB
class FakeUSB:
    def get_path(self):
        return usb_dir

# --- 4️⃣ Synchronisation ---
print("=== Synchronisation vers USB simulé ===")
local_storage.sync(FakeUSB())

# --- 5️⃣ Vérifications ---
usb_files = os.listdir(usb_dir)
local_files = os.listdir(base_path)

print(f"Fichiers sur USB simulé : {usb_files}")
print(f"Fichiers restants localement : {local_files}")

assert "test.csv" in usb_files, "❌ Le fichier n'a pas été copié sur le stockage USB !"
assert "test.csv" not in local_files, "❌ Le fichier local n'a pas été supprimé !"
print("\n✅ Test réussi : fichier copié sur USB et supprimé localement")
