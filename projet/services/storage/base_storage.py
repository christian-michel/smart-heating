"""
base_storage.py

Définit l'interface commune à tous les systèmes de stockage.
(USB, Local, Dropbox, etc.)
"""

from abc import ABC, abstractmethod


class BaseStorage(ABC):

    @abstractmethod
    def is_available(self) -> bool:
        """
        Retourne True si le stockage est disponible et prêt à être utilisé.
        """
        pass

    @abstractmethod
    def get_path(self) -> str:
        """
        Retourne le chemin du dossier où écrire les fichiers.
        """
        pass

    @abstractmethod
    def sync(self, other_storage: "BaseStorage"):
        """
        Synchronise ce stockage avec un autre.
        (Implémentation future)
        """
        pass
