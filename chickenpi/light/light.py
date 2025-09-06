import logging
from chickenpi.light.light_driver import LightDriver, LightState

logger = logging.getLogger(__name__)

light_driver: LightDriver = LightDriver()


def state(driver: LightDriver = light_driver) -> LightState:
    state = driver.get_state()
    return state


def toggle(driver: LightDriver = light_driver) -> LightState:
    state = driver.toggle()
    return state
