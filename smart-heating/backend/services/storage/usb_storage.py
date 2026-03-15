"""
usb_storage.py

Gestion du stockage sur clé USB.
Détection robuste :
- Vérifie que le point est réellement monté
- Vérifie que l'écriture est possible
"""

import os
from backend.services.storage.base_storage import BaseStorage


class USBStorage(BaseStorage):

    def __init__(self, mount_path="/mnt/usb_backup"):
        self.mount_path = mount_path

    def is_available(self) -> bool:
        """
        Vérifie que la clé USB est réellement disponible.

        Conditions :
        1. Le point de montage existe
        2. Il est réellement monté (pas juste un dossier vide)
        3. L'écriture est possible
        """

        # Vérifie que le point de montage existe
        if not os.path.exists(self.mount_path):
            return False

        # Vérifie que c'est un vrai point de montage actif
        if not os.path.ismount(self.mount_path):
            return False

        # Vérifie que l'écriture est possible
        # On utilise un fichier temporaire NON caché
        # car certains systèmes refusent la création
        # de fichiers cachés dans certaines configurations.
        test_file = os.path.join(self.mount_path, "usb_write_test.tmp")

        try:
            with open(test_file, "w") as f:
                f.write("test")

            # Nettoyage du fichier de test
            if os.path.exists(test_file):
                os.remove(test_file)

            return True

        except Exception:
            # Problème d'écriture :
            # - clé montée en lecture seule
            # - clé retirée brutalement
            # - permissions incorrectes
            return False

    def get_path(self) -> str:
        """
        Retourne le chemin du point de montage USB.
        """
        return self.mount_path

    def sync(self, other_storage: BaseStorage):
        """
        Synchronisation future (non implémentée pour l'instant).
        """
        pass