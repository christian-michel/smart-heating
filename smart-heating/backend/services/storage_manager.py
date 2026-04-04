"""
storage_manager.py

Responsabilité :
Gérer dynamiquement le stockage des données :

Priorité :
1. USB
2. Dropbox
3. Local

Synchronisations :
- local → USB (une fois)
- local → Dropbox (une fois)
- USB → Dropbox (périodique)

Objectifs :
- robustesse maximale
- aucune exception bloquante
- comportement prévisible
"""

import time

from backend.services.storage.usb_storage import USBStorage
from backend.services.storage.local_storage import LocalStorage
from backend.services.storage.dropbox_storage import DropboxStorage


class StorageManager:

    def __init__(self):
        self.usb_storage = USBStorage()
        self.dropbox_storage = DropboxStorage()
        self.local_storage = LocalStorage()

        self.active_storage = None

        # Flags pour éviter sync multiples
        self.local_synced_to_usb = False
        self.local_synced_to_dropbox = False

        # Limitation sync Dropbox
        self.last_dropbox_sync = 0
        self.dropbox_sync_interval = 60 # secondes

        self.refresh(initial=True)

    # ==========================
    # === DÉTECTION STOCKAGE
    # ==========================

    def _detect_preferred_storage(self):
        try:
            if self.usb_storage.is_available():
                return self.usb_storage
        except Exception as e:
            print(f"[StorageManager] Erreur USB : {e}")

        try:
            if self.dropbox_storage.is_available():
                return self.dropbox_storage
        except Exception as e:
            print(f"[StorageManager] Erreur Dropbox : {e}")

        return self.local_storage

    def get_active_storage(self):
        return self.active_storage

    # ==========================
    # === REFRESH PRINCIPAL
    # ==========================

    def refresh(self, initial=False):
        preferred_storage = self._detect_preferred_storage()

        # === Initialisation ===
        if self.active_storage is None:
            self.active_storage = preferred_storage

            if isinstance(self.active_storage, USBStorage):
                print("Stockage USB détecté.")
            elif isinstance(self.active_storage, DropboxStorage):
                print("Stockage Dropbox détecté.")
            else:
                print("Mode local (USB et Dropbox indisponibles).")

        # ==========================
        # === SYNCHRONISATIONS
        # ==========================

        self._sync_local_to_usb(preferred_storage)
        self._sync_local_to_dropbox(preferred_storage)
        self._sync_usb_to_dropbox()

        # ==========================
        # === CHANGEMENT ACTIF
        # ==========================

        if type(preferred_storage) != type(self.active_storage):

            if isinstance(preferred_storage, USBStorage):
                print("Bascule → USB")

            elif isinstance(preferred_storage, DropboxStorage):
                print("Bascule → Dropbox")

            else:
                print("Bascule → Local (fallback)")

                # reset flags
                self.local_synced_to_usb = False
                self.local_synced_to_dropbox = False

            self.active_storage = preferred_storage

    # ==========================
    # === SYNC MÉTHODES
    # ==========================

    def _sync_local_to_usb(self, preferred_storage):
        if isinstance(preferred_storage, USBStorage) and not self.local_synced_to_usb:
            try:
                print("Sync local → USB...")
                self.local_storage.sync(self.usb_storage)
                self.local_synced_to_usb = True
            except Exception as e:
                print(f"[StorageManager] Erreur sync local→USB : {e}")

    def _sync_local_to_dropbox(self, preferred_storage):
        if (
            isinstance(preferred_storage, DropboxStorage)
            and not self.local_synced_to_dropbox
        ):
            try:
                print("Sync local → Dropbox...")
                self.local_storage.sync(self.dropbox_storage)
                self.local_synced_to_dropbox = True
            except Exception as e:
                print(f"[StorageManager] Erreur sync local→Dropbox : {e}")

    def _sync_usb_to_dropbox(self):
        current_time = time.time()

        if (
            self._is_usb_available()
            and self._is_dropbox_available()
            and current_time - self.last_dropbox_sync >= self.dropbox_sync_interval
        ):
            try:
                print("Sync USB → Dropbox...")
                self.dropbox_storage.sync(self.usb_storage)
                self.last_dropbox_sync = current_time
            except Exception as e:
                print(f"[StorageManager] Erreur sync USB→Dropbox : {e}")

    # ==========================
    # === HELPERS SAFE
    # ==========================

    def _is_usb_available(self):
        try:
            return self.usb_storage.is_available()
        except Exception:
            return False

    def _is_dropbox_available(self):
        try:
            return self.dropbox_storage.is_available()
        except Exception:
            return False

    # ==========================
    # === FLUSH FINAL (CRITIQUE)
    # ==========================

    def flush_all(self):
        """
        Forcer une synchronisation finale (appelé à l'arrêt du système)
        """
        print("Flush global des stockages...")

        try:
            if self._is_usb_available():
                print("Sync final local → USB")
                self.local_storage.sync(self.usb_storage)
        except Exception as e:
            print(f"[StorageManager] Erreur flush USB : {e}")

        try:
            if self._is_dropbox_available():
                print("Sync final vers Dropbox")
                if self._is_usb_available():
                    self.dropbox_storage.sync(self.usb_storage)
                else:
                    self.dropbox_storage.sync(self.local_storage)
        except Exception as e:
            print(f"[StorageManager] Erreur flush Dropbox : {e}")
