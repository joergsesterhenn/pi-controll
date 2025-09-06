import logging
from chickenpi.door.door_driver import DoorDriver, DoorState

logger = logging.getLogger(__name__)

door_driver: DoorDriver = DoorDriver()


def open_door(driver: DoorDriver = door_driver) -> DoorState:
    if driver.state in (DoorState.OPENING, DoorState.CLOSING):
        logger.info("door is moving")
        return driver.state

    if driver.state == DoorState.OPEN:
        logger.info("door is already open")
        return driver.state
    logger.info("opening door")
    driver.up()
    return driver.state


def close_door(driver: DoorDriver = door_driver) -> DoorState:
    if driver.state in (DoorState.OPENING, DoorState.CLOSING):
        logger.info("door is moving")
        return driver.state

    if driver.state == DoorState.CLOSED:
        logger.info("door is already closed")
        return driver.state
    logger.info("closing door")
    driver.down()
    return driver.state


def coop_door_state(driver: DoorDriver = door_driver) -> DoorState:
    if driver.upper_stop_sensor.value:
        return DoorState.OPEN
    if driver.lower_stop_sensor.value:
        return DoorState.CLOSED
    else:
        return driver.state
