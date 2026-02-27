"""
test_dropbox_storage.py

Tests unitaires pour DropboxStorage (étape C).
Aucune connexion réelle à Dropbox (client mocké).
"""

import os
from unittest.mock import MagicMock, patch
from services.storage.dropbox_storage import DropboxStorage
from services.storage.local_storage import LocalStorage


def test_dropbox_storage_not_available_without_token(monkeypatch):
    monkeypatch.delenv("DROPBOX_TOKEN", raising=False)
    storage = DropboxStorage()
    assert storage.is_available() is False


@patch("services.storage.dropbox_storage.dropbox.Dropbox")
def test_dropbox_storage_upload_csv(mock_dropbox, monkeypatch, tmp_path):
    monkeypatch.setenv("DROPBOX_TOKEN", "fake-token")

    # Mock Dropbox client
    mock_client = MagicMock()
    mock_dropbox.return_value = mock_client

    # Fake local storage
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    test_file = data_dir / "test.csv"
    test_file.write_text("timestamp,temp\n2026-01-01,20")

    local_storage = LocalStorage(base_path=str(data_dir))
    dropbox_storage = DropboxStorage()

    dropbox_storage.sync(local_storage)

    # Vérifie que files_upload a été appelé
    assert mock_client.files_upload.called