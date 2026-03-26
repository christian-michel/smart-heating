"""
dropbox_storage.py

Backend de stockage Dropbox.
Implémentation OAuth 2 moderne (post-2021) avec refresh token.
Upload sécurisé : suppression locale uniquement si l'upload réussit.
Écriture uniquement depuis le storage actif (USB si présent, sinon local data/).
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

        self.configured = all([self.app_key, self.app_secret, self.refresh_token])
        self.client = None

        if self.configured:
            try:
                self.client = dropbox.Dropbox(
                    oauth2_refresh_token=self.refresh_token,
                    app_key=self.app_key,
                    app_secret=self.app_secret
                )
                # Test de connexion
                self.client.users_get_current_account()
                print("✅ DropboxStorage configuré et connecté.")
            except AuthError as e:
                print(f"❌ Dropbox Auth error : {e}")
                self.client = None
                self.configured = False
            except Exception as e:
                print(f"❌ Erreur initialisation Dropbox : {e}")
                self.client = None
                self.configured = False
        else:
            print("❌ DropboxStorage non configuré (vérifier les variables d'environnement).")

    def is_available(self) -> bool:
        """Dropbox est disponible uniquement si correctement configuré et client actif"""
        return self.configured and self.client is not None

    def get_path(self) -> str:
        """
        Chemin logique Dropbox.
        Utilisé uniquement pour interface uniforme avec Logger/StorageManager.
        """
        return "/" # On n'écrit jamais localement ici

    def sync(self, other_storage: BaseStorage):
        """
        Synchronise les fichiers CSV depuis le storage actif (USB ou local data) vers Dropbox.
        Les fichiers sources sont supprimés uniquement si l'upload réussit.
        """
        if not self.is_available():
            print("⚠ DropboxStorage.sync : Dropbox non disponible.")
            return

        source_dir = other_storage.get_path()
        if not os.path.exists(source_dir):
            print(f"⚠ DropboxStorage.sync : dossier source inexistant -> {source_dir}")
            return

        for filename in os.listdir(source_dir):
            if not filename.endswith(".csv"):
                continue

            local_path = os.path.join(source_dir, filename)
            dropbox_path = f"/{filename}" # Upload à la racine Dropbox

            try:
                with open(local_path, "rb") as f:
                    self.client.files_upload(
                        f.read(),
                        dropbox_path,
                        mode=dropbox.files.WriteMode.overwrite
                    )

                print(f"☁️ Dropbox : {filename} uploadé")

                # Suppression du fichier local uniquement après succès upload
                try:
                    os.remove(local_path)
                    print(f"🗑 Local supprimé : {filename}")
                except Exception as e:
                    print(f"⚠ Erreur suppression locale ({filename}) : {e}")

            except AuthError as e:
                print(f"❌ Dropbox Auth error ({filename}) : {e}")
            except ApiError as e:
                print(f"❌ Dropbox API error ({filename}) : {e}")
            except Exception as e:
                print(f"❌ Dropbox error ({filename}) : {e}")
