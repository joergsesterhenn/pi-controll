import logging

from chickenpi.door.door_driver import DoorDriver, DoorState

logger = logging.getLogger(__name__)

driver = DoorDriver()


def open_door(driver: DoorDriver = driver):
    if driver.state in (DoorState.OPENING, DoorState.CLOSING):
        logger.info("door is moving")
        return {"status": driver.state.name}

    if driver.state == DoorState.OPEN:
        logger.info("door is already open")
        return {"status": driver.state.name}
    logger.info("opening door")
    driver.up()
    return {"status": driver.state.name}


def close_door(driver: DoorDriver = driver):
    if driver.state in (DoorState.OPENING, DoorState.CLOSING):
        logger.info("door is moving")
        return {"status": driver.state.name}

    if driver.state == DoorState.CLOSED:
        logger.info("door is already closed")
        return {"status": driver.state.name}
    logger.info("closing door")
    driver.down()
    return {"status": driver.state.name}


def coop_door_state(driver: DoorDriver = driver):
    if driver.upper_stop_sensor.value:
        return {"status": DoorState.OPEN.value}
    if driver.lower_stop_sensor.value:
        return {"status": DoorState.CLOSED.value}
    else:
        return {"status": driver.state.value}
