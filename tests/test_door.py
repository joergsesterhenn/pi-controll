from chickenpi.door.door import coop_door_state, close_door, open_door
from chickenpi.door.door_driver import DoorDriver, DoorState
from unittest.mock import patch


def test_open_door_open():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPEN
    assert open_door(driver) == DoorState.OPEN


def test_open_door_opening():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPENING
    assert open_door(driver) == DoorState.OPENING


def test_open_door_closing():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSING
    assert open_door(driver) == DoorState.CLOSING


@patch("chickenpi.door.door_driver.DigitalInputDevice.wait_for_active", return_value=True)
def test_open_door_closed(mock_wait_for_active):
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSED
    assert open_door(driver) == DoorState.OPENING


def test_close_door_closed():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSED
    assert close_door(driver) == DoorState.CLOSED


def test_close_door_closing():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSING
    assert close_door(driver) == DoorState.CLOSING


def test_close_door_opening():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPENING
    assert close_door(driver) == DoorState.OPENING


@patch("chickenpi.door.door_driver.DigitalInputDevice.wait_for_active", return_value=True)
def test_close_door_open(mock_wait_for_active):
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPEN
    assert close_door(driver) == DoorState.CLOSING


def test_coop_door_state_undefined():
    driver = DoorDriver(door_wait_time=0)
    assert coop_door_state(driver) == DoorState.UNDEFINED


def test_coop_door_state_state_up():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPEN
    assert coop_door_state(driver) == DoorState.OPEN


def test_coop_door_state_state_down():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSED
    assert coop_door_state(driver) == DoorState.CLOSED


def test_coop_door_state_upper():
    driver = DoorDriver(door_wait_time=0)
    driver.upper_stop_sensor._fire_events(ticks=1, new_active=1)
    assert coop_door_state(driver) == DoorState.OPEN


def test_coop_door_state_lower():
    driver = DoorDriver(door_wait_time=0)
    driver.lower_stop_sensor._fire_events(ticks=1, new_active=1)
    assert coop_door_state(driver) == DoorState.CLOSED


def test_door_driver_initial_state_is_undefined():
    driver = DoorDriver(door_wait_time=0)
    assert driver.state == DoorState.UNDEFINED


@patch("chickenpi.door.door_driver.DigitalInputDevice.wait_for_active", return_value=False)
def test_up_timeout_sets_error(mock_wait_for_active):
    driver = DoorDriver(door_wait_time=1)
    driver.state = DoorState.UNDEFINED
    driver.up()
    assert driver.state == DoorState.ERROR


@patch("chickenpi.door.door_driver.DigitalInputDevice.wait_for_active", return_value=False)
def test_down_timeout_sets_error(mock_wait_for_active):
    driver = DoorDriver(door_wait_time=1)
    driver.state = DoorState.UNDEFINED
    driver.down()
    assert driver.state == DoorState.ERROR
