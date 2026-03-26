"""
test_base_storage.py

Tests pour vérifier le bon fonctionnement de l'interface BaseStorage.
"""

import pytest
from services.storage.base_storage import BaseStorage


def test_base_storage_is_abstract():
    """
    Vérifie que BaseStorage ne peut pas être instancié directement.
    """
    with pytest.raises(TypeError):
        BaseStorage()


class DummyStorage(BaseStorage):
    """
    Implémentation minimale pour tester l'interface.
    """

    def is_available(self) -> bool:
        return True

    def get_path(self) -> str:
        return "/tmp"

    def sync(self, other_storage: BaseStorage):
        pass


def test_dummy_storage_works():
    """
    Vérifie qu'une implémentation concrète fonctionne correctement.
    """
    dummy = DummyStorage()

    assert dummy.is_available() is True
    assert dummy.get_path() == "/tmp"