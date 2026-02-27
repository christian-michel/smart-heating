"""
storage_manager.py

Sélectionne automatiquement le stockage actif :
- USB si disponible
- Sinon stockage local

Affiche un message uniquement si le stockage change
et déclenche la synchronisation local -> USB dès que l'USB devient disponible.
"""

from services.storage.usb_storage import USBStorage
from services.storage.local_storage import LocalStorage


class StorageManager:

    def __init__(self):
        self.usb_storage = USBStorage()
        self.local_storage = LocalStorage()
        self.active_storage = None

        # Indique si les données locales ont déjà été synchronisées vers l'USB
        self.local_synced_to_usb = False

        self.refresh(initial=True)

    def _detect_preferred_storage(self):
        """
        Détermine quel stockage devrait être actif.
        """
        if self.usb_storage.is_available():
            return self.usb_storage
        return self.local_storage

    def get_active_storage(self):
        """
        Retourne le stockage actuellement utilisé.
        """
        return self.active_storage

    def refresh(self, initial=False):
        """
        Vérifie si le stockage doit changer.
        Déclenche la synchronisation locale -> USB dès que l'USB devient disponible.
        """

        preferred_storage = self._detect_preferred_storage()

        # === Premier lancement ===
        if self.active_storage is None:
            self.active_storage = preferred_storage
            if isinstance(self.active_storage, USBStorage):
                print("Stockage USB détecté.")
            else:
                print("USB non disponible. Utilisation du stockage local.")
            return

        # === USB devient disponible (sync garantie) ===
        if isinstance(preferred_storage, USBStorage) and not self.local_synced_to_usb:
            print("USB disponible. Synchronisation des données locales vers USB...")
            self.local_storage.sync(self.usb_storage)
            self.local_synced_to_usb = True

        # === Changement réel de stockage ===
        if type(preferred_storage) != type(self.active_storage):

            if isinstance(preferred_storage, USBStorage):
                print("Bascule vers stockage USB.")
            else:
                print("Clé USB retirée. Bascule vers stockage local.")
                # On réinitialise pour la prochaine insertion
                self.local_synced_to_usb = False

            self.active_storage = preferred_storage