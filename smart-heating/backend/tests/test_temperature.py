from backend.core.temperature import TemperatureSensor


def test_valid_temperature(monkeypatch):
    sensor = TemperatureSensor()

    def fake_read():
        return [
            "aa bb cc YES\n",
            "xx yy t=21562\n"
        ]

    monkeypatch.setattr(sensor, "_read_raw", fake_read)

    temp = sensor.get_temperature()
    assert temp == 21.56


def test_crc_error_with_fallback(monkeypatch):
    sensor = TemperatureSensor()
    sensor.last_valid_temperature = 20.0

    def fake_read():
        return [
            "aa bb cc NO\n",
            "xx yy t=99999\n"
        ]

    monkeypatch.setattr(sensor, "_read_raw", fake_read)

    temp = sensor.get_temperature()
    assert temp == 20.0


def test_no_data_returns_none(monkeypatch):
    sensor = TemperatureSensor()

    def fake_read():
        raise RuntimeError("fail")

    monkeypatch.setattr(sensor, "_read_raw", fake_read)

    temp = sensor.get_temperature()
    assert temp is None