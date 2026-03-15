from backend.services.logger_service import LoggerService
import time

logger = LoggerService()

for i in range(12):
    logger.log(22.5 + i*0.1, heating_state=(i%2==0), switch_state=(i%3==0))
    time.sleep(1)

logger.close()
print("Test Logger terminé")
