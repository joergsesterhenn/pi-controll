import logging

from chickenpi.lights.lights_driver import LightsDriver

logger = logging.getLogger(__name__)

driver: LightsDriver = LightsDriver()


def toggle(driver: LightsDriver):
    state = driver.toggle()
    return {
        "status": state,
    }


def state(driver: LightsDriver):
    state = driver.get_state()
    return {
        "on": state.value == 1,
    }
