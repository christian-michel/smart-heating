from backend.services.logger_service import LoggerService
import os

def test_logger_writes_file(tmp_path):
    """
    Test simple :
    - écrit quelques lignes
    - vérifie qu'un fichier est créé
    """

    logger = LoggerService(base_path=tmp_path)

    logger.log(22.5, heating_state=True, switch_state=False)
    logger.log(23.0, heating_state=False, switch_state=True)

    logger.close()

    files = list(tmp_path.glob("*.csv"))

    assert len(files) > 0