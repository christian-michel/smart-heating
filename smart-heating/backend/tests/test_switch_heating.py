from backend.core.switch import Switch
from backend.core.heating import HeatingSystem
import time

switch = Switch()
heating = HeatingSystem()

print("Test switch + heating")

while True:

    if switch.is_on():
        heating.turn_on()
        print("Switch ON → chauffage ON")

    else:
        heating.turn_off()
        print("Switch OFF → chauffage OFF")

    time.sleep(0.5)
