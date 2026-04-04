import pytest

from backend.core.heating import HeatingSystem


class FakeLED:
    """
    Simulation de la LED pour les tests.
    Permet d'éviter toute dépendance au GPIO réel.
    """
    def __init__(self):
        self.is_lit = False

    def on(self):
        self.is_lit = True

    def off(self):
        self.is_lit = False


def test_heating_turn_on_off(monkeypatch):
    """
    Test basique :
    - allumer
    - éteindre
    """

    # Remplace LED par FakeLED
    monkeypatch.setattr("backend.core.heating.LED", lambda pin: FakeLED())

    heating = HeatingSystem()

    heating.turn_on()
    assert heating.is_on() is True

    heating.turn_off()
    assert heating.is_on() is False


def test_heating_idempotent(monkeypatch):
    """
    Vérifie que plusieurs appels ON/OFF ne cassent pas l'état.
    """

    monkeypatch.setattr("backend.core.heating.LED", lambda pin: FakeLED())

    heating = HeatingSystem()

    heating.turn_on()
    heating.turn_on() # appel doublon
    assert heating.is_on() is True

    heating.turn_off()
    heating.turn_off() # appel doublon
    assert heating.is_on() is False


def test_heating_simulation_mode(monkeypatch):
    """
    Test si le GPIO est indisponible.
    """

    # Simule absence de GPIO
    monkeypatch.setattr("backend.core.heating.GPIO_AVAILABLE", False)

    heating = HeatingSystem()

    heating.turn_on()
    assert heating.is_on() is True

    heating.turn_off()
    assert heating.is_on() is False