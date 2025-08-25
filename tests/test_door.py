from chickenpi.door import DoorState, close_door, coop_door_state, open_door
from gpiozero.pins.mock import MockPin, MockFactory

from chickenpi.door_driver import DoorDriver


def test_open_door_open():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPEN
    assert open_door(driver) == {"status": DoorState.OPEN.name}


def test_open_door_opening():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPENING
    assert open_door(driver) == {"status": DoorState.OPENING.name}


def test_open_door_closing():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSING
    assert open_door(driver) == {"status": DoorState.CLOSING.name}


def test_open_door_closed():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSED
    assert open_door(driver) == {"status": DoorState.OPENING.name}


def test_close_door_closed():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSED
    assert close_door(driver) == {"status": DoorState.CLOSED.name}


def test_close_door_closing():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSING
    assert close_door(driver) == {"status": DoorState.CLOSING.name}


def test_close_door_opening():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPENING
    assert close_door(driver) == {"status": DoorState.OPENING.name}


def test_close_door_open():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPEN
    assert close_door(driver) == {"status": DoorState.CLOSING.name}


def test_coop_door_state_undefined():
    driver = DoorDriver(door_wait_time=0)
    assert coop_door_state(driver) == {"status": 0}


def test_coop_door_state_state_up():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.OPEN
    assert coop_door_state(driver) == {"status": 1}


def test_coop_door_state_state_down():
    driver = DoorDriver(door_wait_time=0)
    driver.state = DoorState.CLOSED
    assert coop_door_state(driver) == {"status": 2}


def test_coop_door_state_upper():
    driver = DoorDriver(door_wait_time=0)
    driver.upper_stop_sensor._fire_events(ticks=1, new_active=1)
    assert coop_door_state(driver) == {"status": 1}


def test_coop_door_state_lower():
    driver = DoorDriver(door_wait_time=0)
    driver.lower_stop_sensor._fire_events(ticks=1, new_active=1)
    assert coop_door_state(driver) == {"status": 2}
