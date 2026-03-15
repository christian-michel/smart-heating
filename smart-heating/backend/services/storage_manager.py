"""
storage_manager.py

Sélectionne automatiquement le stockage actif :
- USB si disponible
- Sinon Dropbox si disponible
- Sinon stockage local

Synchronisations :
- local -> USB
- local -> Dropbox
- USB -> Dropbox (opportuniste)
"""

from backend.services.storage.usb_storage import USBStorage
from backend.services.storage.local_storage import LocalStorage
from backend.services.storage.dropbox_storage import DropboxStorage


class StorageManager:

    def __init__(self):
        self.usb_storage = USBStorage()
        self.dropbox_storage = DropboxStorage()
        self.local_storage = LocalStorage()
        self.active_storage = None

        # Flags uniquement pour éviter double sync local
        self.local_synced_to_usb = False
        self.local_synced_to_dropbox = False

        self.refresh(initial=True)

    def _detect_preferred_storage(self):
        if self.usb_storage.is_available():
            return self.usb_storage
        if self.dropbox_storage.is_available():
            return self.dropbox_storage
        return self.local_storage

    def get_active_storage(self):
        return self.active_storage

    def refresh(self, initial=False):
        preferred_storage = self._detect_preferred_storage()

        # === Premier lancement ===
        if self.active_storage is None:
            self.active_storage = preferred_storage

            if isinstance(self.active_storage, USBStorage):
                print("Stockage USB détecté.")
            elif isinstance(self.active_storage, DropboxStorage):
                print("Stockage Dropbox détecté.")
            else:
                print("USB et Dropbox non disponibles. Utilisation du stockage local.")

            # IMPORTANT : on ne return plus ici

        # === Local -> USB ===
        if isinstance(preferred_storage, USBStorage) and not self.local_synced_to_usb:
            print("USB disponible. Synchronisation des données locales vers USB...")
            self.local_storage.sync(self.usb_storage)
            self.local_synced_to_usb = True

        # === Local -> Dropbox (si pas USB) ===
        if (
            isinstance(preferred_storage, DropboxStorage)
            and not self.local_synced_to_dropbox
        ):
            print("Dropbox disponible. Synchronisation des données locales vers Dropbox...")
            self.local_storage.sync(self.dropbox_storage)
            self.local_synced_to_dropbox = True

        # === USB -> Dropbox (toujours tenté si dispo) ===
        if self.usb_storage.is_available() and self.dropbox_storage.is_available():
            print("Synchronisation des données USB vers Dropbox...")
            self.dropbox_storage.sync(self.usb_storage)

        # === Changement réel de stockage actif ===
        if type(preferred_storage) != type(self.active_storage):

            if isinstance(preferred_storage, USBStorage):
                print("Bascule vers stockage USB.")

            elif isinstance(preferred_storage, DropboxStorage):
                print("Bascule vers stockage Dropbox.")

            else:
                print("Stockage distant indisponible. Bascule vers stockage local.")

                # reset flags si on retombe en local
                self.local_synced_to_usb = False
                self.local_synced_to_dropbox = False

            self.active_storage = preferred_storage