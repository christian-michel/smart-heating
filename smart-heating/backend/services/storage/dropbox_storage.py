"""
dropbox_storage.py

Backend de stockage Dropbox.
Implémentation OAuth 2 moderne (post-2021) avec refresh token.
Upload sécurisé : suppression locale uniquement si l'upload réussit.
"""

import os
import dropbox
from dropbox.exceptions import ApiError, AuthError
from backend.services.storage.base_storage import BaseStorage


class DropboxStorage(BaseStorage):

    def __init__(self):
        """
        Initialise DropboxStorage via OAuth 2 avec refresh token.

        Variables d'environnement requises :
        - DROPBOX_APP_KEY
        - DROPBOX_APP_SECRET
        - DROPBOX_REFRESH_TOKEN
        """

        self.app_key = os.getenv("DROPBOX_APP_KEY")
        self.app_secret = os.getenv("DROPBOX_APP_SECRET")
        self.refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")

        self.configured = all([
            self.app_key,
            self.app_secret,
            self.refresh_token
        ])

        if self.configured:
            # Le SDK Dropbox gère automatiquement le refresh du token
            self.client = dropbox.Dropbox(
                oauth2_refresh_token=self.refresh_token,
                app_key=self.app_key,
                app_secret=self.app_secret
            )
        else:
            self.client = None

    def is_available(self) -> bool:
        """
        Dropbox est disponible uniquement si correctement configuré.
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
        Les fichiers sources sont supprimés uniquement si l'upload réussit.
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

            success = False

            try:
                with open(local_path, "rb") as f:
                    self.client.files_upload(
                        f.read(),
                        dropbox_path,
                        mode=dropbox.files.WriteMode.overwrite
                    )

                print(f"☁️ Dropbox : {filename} uploadé")
                success = True

            except AuthError as e:
                print(f"Dropbox Auth error ({filename}) : {e}")

            except ApiError as e:
                print(f"Dropbox API error ({filename}) : {e}")

            except Exception as e:
                print(f"Dropbox error ({filename}) : {e}")

            # Suppression uniquement si upload réussi
            if success:
                try:
                    os.remove(local_path)
                    print(f"Local supprimé : {filename}")
                except Exception as e:
                    print(f"Erreur suppression locale ({filename}) : {e}")