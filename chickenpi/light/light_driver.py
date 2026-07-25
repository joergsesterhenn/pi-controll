import logging
from enum import IntEnum
from threading import Lock

from gpiozero import OutputDevice
from pydantic import BaseModel

from chickenpi.device.factory import get_device_factory

logger = logging.getLogger("app")


class LightState(IntEnum):
    OFF, ON, UNDEFINED = range(3)


class Light(BaseModel):
    status: LightState


class LightDriver:
    def __init__(self, relay_1_pin: int = 18):
        self.lock = Lock()
        self.state = LightState.UNDEFINED
        self.relay_1: OutputDevice | None = None
        self.relay_1_pin = relay_1_pin

    def toggle(self) -> LightState:
        with self.lock:
            self.relay = self.get_relay()
            self.relay_1.toggle()
            self.state = LightState(self.relay_1.value)
            return self.state

    def get_state(self) -> LightState:
        with self.lock:
            self.relay = self.get_relay()
            self.state = LightState(self.relay_1.value)
            return self.state

    def get_relay(self) -> OutputDevice:
        if self.relay_1 is None:
            self.relay_1 = OutputDevice(
                self.relay_1_pin,
                active_high=False,
                initial_value=None,
                pin_factory=get_device_factory(),
            )
            logger.info(
                f"Initializing relay1 (active_high=False, is_active={self.relay_1.is_active()})"
            )
        return self.relay_1
