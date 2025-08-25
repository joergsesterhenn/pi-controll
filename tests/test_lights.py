from chickenpi.lights import state, toggle
from chickenpi.lights_driver import LightsDriver


def test_toggle():
    driver = LightsDriver()
    assert toggle(driver) == {"status": "ON"}


def test_state():
    driver = LightsDriver()
    assert state(driver) == {"on": False}
