"""
storage_manager.py

Sélectionne automatiquement le stockage actif :
- USB si disponible
- Sinon stockage local

Affiche un message uniquement si le stockage change.
"""

from services.storage.usb_storage import USBStorage
from services.storage.local_storage import LocalStorage


class StorageManager:

    def __init__(self):
        self.usb_storage = USBStorage()
        self.local_storage = LocalStorage()
        self.active_storage = None
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
        Affiche un message uniquement si changement réel.
        """

        preferred_storage = self._detect_preferred_storage()

        # Premier lancement
        if self.active_storage is None:
            self.active_storage = preferred_storage
            if isinstance(self.active_storage, USBStorage):
                print("Stockage USB détecté.")
            else:
                print("USB non disponible. Utilisation du stockage local.")
            return

        # Si changement réel de stockage
        if type(preferred_storage) != type(self.active_storage):

            if isinstance(preferred_storage, USBStorage):
                print("Clé USB insérée. Bascule vers stockage USB.")
            else:
                print("Clé USB retirée. Bascule vers stockage local.")

            self.active_storage = preferred_storage