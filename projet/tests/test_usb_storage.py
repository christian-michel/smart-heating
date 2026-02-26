"""
test_usb_storage.py

Tests pour vérifier le bon fonctionnement du module USBStorage.
"""

import os
import tempfile
from services.storage.usb_storage import USBStorage


def test_usb_storage_available_when_path_exists(tmp_path):
    """
    Vérifie que USBStorage est disponible si le chemin existe.
    """

    # Création d'un faux dossier temporaire
    fake_usb_path = tmp_path / "usb_backup"
    fake_usb_path.mkdir()

    storage = USBStorage(str(fake_usb_path))

    assert storage.is_available() is True
    assert storage.get_path() == str(fake_usb_path)


def test_usb_storage_unavailable_when_path_missing(tmp_path):
    """
    Vérifie que USBStorage n'est pas disponible si le chemin n'existe pas.
    """

    fake_usb_path = tmp_path / "usb_backup"

    storage = USBStorage(str(fake_usb_path))

    assert storage.is_available() is False


def test_usb_storage_creates_file(tmp_path):
    """
    Vérifie qu'on peut écrire un fichier dans le stockage USB.
    """

    fake_usb_path = tmp_path / "usb_backup"
    fake_usb_path.mkdir()

    storage = USBStorage(str(fake_usb_path))

    test_file = os.path.join(storage.get_path(), "test.csv")

    with open(test_file, "w") as f:
        f.write("temperature,etat\n20,ON\n")

    assert os.path.exists(test_file)
