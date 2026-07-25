import pytest
from chickenpi.temperature.temperature import Temperature, get_readings


def test_get_readings():
    assert get_readings("tests/data/temperature/") == Temperature(
        inside=12.5, outside=-12.1
    )


def test_get_readings_empty():
    with pytest.raises(Exception):
        get_readings()


def test_get_readings_error():
    with pytest.raises(Exception):
        get_readings("tests/data/temperature_broken/")
