import logging
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero.exc import PinUnknownPi
from gpiozero import Device, OutputDevice
from lgpio import gpiochip_open, gpio_read, gpiochip_close, error
from threading import Lock
from enum import Enum

logger = logging.getLogger("app")


class LightState(Enum):
    OFF, ON, UNDEFINED = range(3)


class LightsDriver:
    def __init__(self, relay_1_pin: int = 18):
        self.lock = Lock()
        self.state = LightState.UNDEFINED
        self.initialize_device_factory()
        self.relay_1: OutputDevice | None = None
        self.relay_1_pin = relay_1_pin

    def initialize_device_factory(self, type=""):
        try:
            Device.pin_factory = LGPIOFactory()
        except PinUnknownPi:
            Device.pin_factory = MockFactory(
                pin_class=MockPWMPin if type == "PWM" else None
            )

    def toggle(self):
        with self.lock:
            self.relay = self.get_relay()
            self.relay_1.toggle()
            self.state = LightState(self.relay_1.value)
            return self.state.name

    def get_state(self):
        with self.lock:
            self.relay = self.get_relay()
            self.state = LightState(self.relay_1.value)
            return self.state

    def get_relay(self) -> OutputDevice:
        if self.relay_1 is None:
            try:
                initial_value = False if get_current_state() else True
            except error:
                logger.error("Failed to read initial value.")
                initial_value = False
            logger.info(f"Initializing relay1 with value={initial_value}")
            self.relay_1 = OutputDevice(
                18, active_high=False, initial_value=initial_value
            )
        return self.relay_1


def get_current_state():
    chip0 = gpiochip_open(0)
    current = gpio_read(chip0, 18)
    gpiochip_close(chip0)
    return current
