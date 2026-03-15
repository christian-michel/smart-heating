"""
test_local_storage.py

Tests pour vérifier le bon fonctionnement de LocalStorage.
"""

import os
from services.storage.local_storage import LocalStorage


def test_local_storage_always_available(tmp_path):
    """
    Vérifie que LocalStorage est toujours disponible.
    """

    storage = LocalStorage(str(tmp_path))

    assert storage.is_available() is True


def test_local_storage_creates_directory(tmp_path):
    """
    Vérifie que le dossier est créé automatiquement.
    """

    test_path = tmp_path / "local_data"

    storage = LocalStorage(str(test_path))

    assert os.path.exists(storage.get_path())


def test_local_storage_can_write_file(tmp_path):
    """
    Vérifie qu'on peut écrire un fichier dans le stockage local.
    """

    storage = LocalStorage(str(tmp_path))

    file_path = os.path.join(storage.get_path(), "test.csv")

    with open(file_path, "w") as f:
        f.write("temperature,etat\n21,OFF\n")

    assert os.path.exists(file_path)
