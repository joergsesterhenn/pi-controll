from chickenpi.lights.lights import state, toggle
from chickenpi.lights.lights_driver import LightsDriver


def test_toggle():
    driver = LightsDriver()
    assert toggle(driver) == {"status": "ON"}


def test_toggle_off():
    driver = LightsDriver()
    toggle(driver)
    assert toggle(driver) == {"status": "OFF"}


def test_state():
    driver = LightsDriver()
    assert state(driver) == {"on": False}
