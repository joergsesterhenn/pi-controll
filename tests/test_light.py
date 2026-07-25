from unittest.mock import MagicMock
from chickenpi.light.light import state, toggle
from chickenpi.light.light_driver import LightDriver, LightState


def test_toggle():
    driver = LightDriver()
    driver.state = LightState.OFF
    driver.relay_1 = MagicMock()
    driver.relay_1.value = 1
    assert toggle(driver) == LightState.ON


def test_toggle_off():
    driver = LightDriver()
    driver.relay_1 = MagicMock()
    driver.relay_1.value = 0
    assert toggle(driver) == LightState.OFF


def test_state_off():
    driver = LightDriver()
    driver.relay_1 = MagicMock()
    driver.relay_1.value = 0
    assert state(driver) == LightState.OFF


def test_state_on():
    driver = LightDriver()
    driver.relay_1 = MagicMock()
    driver.relay_1.value = 1
    assert state(driver) == LightState.ON


def test_state_undefined():
    driver = LightDriver()
    assert state(driver) == LightState.OFF
