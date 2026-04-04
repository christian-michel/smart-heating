"""
test_logger_service.py

Test autonome de LoggerService :
- Buffer RAM
- Flush automatique (taille / temps)
- Flush final intelligent (USB → local)
- Synchronisation (mock Dropbox)
"""

import os
import shutil
import time

from backend.services.logger_service import LoggerService

# === Mock StorageManager pour tests ===
class MockStorage:
    def __init__(self, path, available=True):
        self.path = path
        self.available = available
    def get_path(self):
        return self.path
    def is_available(self):
        return self.available

class MockStorageManager:
    def __init__(self, usb_available=True, dropbox_available=True):
        self.usb_storage = MockStorage("/tmp/mock_usb", usb_available)
        self.local_storage = MockStorage("/tmp/mock_local")
        self.dropbox_storage = MockStorage("/tmp/mock_dropbox", dropbox_available)
    def get_active_storage(self):
        # Retourne USB si dispo, sinon local
        return self.usb_storage if self.usb_storage.is_available() else self.local_storage
    def refresh(self):
        print("[MockStorageManager] Synchronisation simulée")

# === Test LoggerService ===
def test_logger_service():
    # Nettoyage anciens fichiers test
    for folder in ["/tmp/mock_usb", "/tmp/mock_local"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

    print("\n=== TEST LoggerService avec USB disponible ===")
    logger = LoggerService(base_path=None, enable_sync=True)
    logger.storage_manager = MockStorageManager(usb_available=True)

    # Log de plusieurs entrées
    for i in range(7):
        logger.log(temperature=20+i*0.1, heating_state=(i%2==0), switch_state=(i%3==0))
        time.sleep(0.1)

    # Flush final
    logger.close()

    print("\n=== Vérification des fichiers ===")
    print("USB :", os.listdir("/tmp/mock_usb"))
    print("Local :", os.listdir("/tmp/mock_local"))

    print("\n=== TEST LoggerService sans USB (fallback local) ===")
    logger2 = LoggerService(base_path=None, enable_sync=True)
    logger2.storage_manager = MockStorageManager(usb_available=False)
    for i in range(3):
        logger2.log(temperature=25+i*0.2, heating_state=True, switch_state=False)
        time.sleep(0.1)
    logger2.close()

    print("\n=== Vérification des fichiers fallback ===")
    print("USB :", os.listdir("/tmp/mock_usb"))
    print("Local :", os.listdir("/tmp/mock_local"))

if __name__ == "__main__":
    test_logger_service()
