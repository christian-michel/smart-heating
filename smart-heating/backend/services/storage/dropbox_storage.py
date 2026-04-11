"""
dropbox_storage.py

Responsabilité :
Backend de stockage Dropbox.

Fonctionnement :
- Auth via OAuth2 refresh token
- Upload des fichiers CSV
- Suppression locale uniquement si upload réussi

Robustesse :
- Aucun crash bloquant
- Logs explicites
"""

import os
import dropbox
from dropbox.exceptions import ApiError, AuthError

from backend.services.storage.base_storage import BaseStorage


class DropboxStorage(BaseStorage):

    def __init__(self):
        """
        Initialise Dropbox via variables d'environnement.
        """

        # ==========================
        # === VARIABLES ENV
        # ==========================
        self.app_key = os.getenv("DROPBOX_APP_KEY")
        self.app_secret = os.getenv("DROPBOX_APP_SECRET")
        self.refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")

        self.configured = all([
            self.app_key,
            self.app_secret,
            self.refresh_token
        ])

        self.client = None

        if not self.configured:
            print("❌ DropboxStorage non configuré (variables d'environnement manquantes)")
            return

        # ==========================
        # === INIT CLIENT
        # ==========================
        try:
            self.client = dropbox.Dropbox(
                oauth2_refresh_token=self.refresh_token,
                app_key=self.app_key,
                app_secret=self.app_secret
            )

            # Test réel connexion
            self.client.users_get_current_account()

            print("✅ Dropbox connecté avec succès")

        except AuthError as e:
            print(f"❌ Auth Dropbox échouée : {e}")
            self.client = None
            self.configured = False

        except Exception as e:
            print(f"❌ Erreur init Dropbox : {e}")
            self.client = None
            self.configured = False

    # ==========================
    # === DISPONIBILITÉ
    # ==========================
    def is_available(self) -> bool:
        return self.configured and self.client is not None

    # ==========================
    # === PATH (LOGIQUE)
    # ==========================
    def get_path(self) -> str:
        return "/"

    # ==========================
    # === SYNC
    # ==========================
    def sync(self, other_storage: BaseStorage):
        """
        Synchronise fichiers CSV vers Dropbox.
        """

        if not self.is_available():
            print("⚠ Dropbox indisponible → sync ignorée")
            return

        source_dir = other_storage.get_path()

        if not os.path.exists(source_dir):
            print(f"⚠ Dossier source inexistant : {source_dir}")
            return

        print(f"[Dropbox] Sync depuis : {source_dir}")

        for filename in os.listdir(source_dir):

            # On ne traite que les CSV
            if not filename.endswith(".csv"):
                continue

            local_path = os.path.join(source_dir, filename)
            dropbox_path = f"/{filename}"

            # Sécurité : éviter fichiers vides ou inexistants
            if not os.path.isfile(local_path):
                continue

            try:
                with open(local_path, "rb") as f:
                    self.client.files_upload(
                        f.read(),
                        dropbox_path,
                        mode=dropbox.files.WriteMode.overwrite
                    )

                print(f"☁️ Upload OK : {filename}")

                # ==========================
                # === SUPPRESSION LOCALE
                # ==========================
                try:
                    os.remove(local_path)
                    print(f"🗑 Supprimé local : {filename}")
                except Exception as e:
                    print(f"⚠ Impossible de supprimer {filename} : {e}")

            except AuthError as e:
                print(f"❌ Auth error ({filename}) : {e}")

            except ApiError as e:
                print(f"❌ API error ({filename}) : {e}")

            except Exception as e:
                print(f"❌ Erreur upload ({filename}) : {e}")