from chickenpi.door.door import coop_door_state, close_door, open_door
from chickenpi.door.door_driver import DoorDriver, DoorState


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


def test_open_door_closed():
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


def test_close_door_open():
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
