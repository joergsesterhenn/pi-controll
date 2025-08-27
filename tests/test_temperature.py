from chickenpi.temperature.temperature import get_readings


def test_get_readings_empty():
    assert get_readings() == {}


def test_get_readings():
    assert get_readings("tests/data/temperature/") == {"inside": 12.5, "outside": -12.1}
