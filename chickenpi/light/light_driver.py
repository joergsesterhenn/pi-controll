import logging
from gpiozero import OutputDevice
from lgpio import gpiochip_open, gpio_read, gpiochip_close
from threading import Lock
from enum import IntEnum

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
            initial_value = False if self.get_current_state(self.relay_1_pin) else True
            logger.info(f"Initializing relay1 with value={initial_value}")
            self.relay_1 = OutputDevice(
                self.relay_1_pin,
                active_high=False,
                initial_value=initial_value,
                pin_factory=get_device_factory(),
            )
        return self.relay_1

    @staticmethod
    def get_current_state(pin):
        try:
            chip0 = gpiochip_open(0)
            current = gpio_read(chip0, pin)
            gpiochip_close(chip0)
            return current
        except Exception:
            logger.exception("Failed to read initial value.")
            return True
