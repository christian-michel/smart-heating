"""
dropbox_storage.py

Backend de stockage Dropbox (étape C).
Upload réel des fichiers CSV via l'API Dropbox.
"""

import os
import dropbox
from dropbox.exceptions import ApiError
from services.storage.base_storage import BaseStorage


class DropboxStorage(BaseStorage):

    def __init__(self):
        """
        Initialise DropboxStorage à partir de la variable d'environnement.
        """
        self.token = os.getenv("DROPBOX_TOKEN")
        self.configured = bool(self.token)
        self.client = dropbox.Dropbox(self.token) if self.configured else None

    def is_available(self) -> bool:
        """
        Dropbox est disponible uniquement s'il est configuré.
        """
        return self.configured

    def get_path(self) -> str:
        """
        Chemin logique Dropbox.
        """
        return "dropbox://"

    def sync(self, other_storage: BaseStorage):
        """
        Synchronise les fichiers CSV depuis un stockage local ou USB vers Dropbox.
        """

        if not self.is_available():
            return

        source_dir = other_storage.get_path()

        if not os.path.exists(source_dir):
            return

        for filename in os.listdir(source_dir):

            if not filename.endswith(".csv"):
                continue

            local_path = os.path.join(source_dir, filename)
            dropbox_path = f"/{filename}"

            try:
                with open(local_path, "rb") as f:
                    self.client.files_upload(
                        f.read(),
                        dropbox_path,
                        mode=dropbox.files.WriteMode.overwrite
                    )
                print(f"Dropbox : {filename} uploadé")

            except ApiError as e:
                print(f"Dropbox API error ({filename}) : {e}")

            except Exception as e:
                print(f"Dropbox error ({filename}) : {e}")