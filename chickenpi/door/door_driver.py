from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero.exc import PinUnknownPi
from gpiozero import Device, Motor, DigitalInputDevice
from threading import Lock
from enum import Enum


class DoorState(Enum):
    UNDEFINED, OPEN, CLOSED, OPENING, CLOSING = range(5)


class DoorDriver:
    def __init__(
        self,
        door_motor_down_pin: int = 22,
        door_motor_up_pin: int = 17,
        door_motor_enabled_pin: int = 23,
        door_wait_time: int = 10,
        upper_stop_pin: int = 6,
        lower_stop_pin: int = 19,
    ):
        self.lock = Lock()
        self.state = DoorState.UNDEFINED
        self.initialize_device_factory(type="PWM")
        self.motor = Motor(
            forward=door_motor_down_pin,
            backward=door_motor_up_pin,
            enable=door_motor_enabled_pin,
        )
        self.upper_stop_sensor = DigitalInputDevice(pin=upper_stop_pin)
        self.upper_stop_sensor.when_activated = self.opened
        self.lower_stop_sensor = DigitalInputDevice(pin=lower_stop_pin)
        self.lower_stop_sensor.when_activated = self.closed
        self.door_wait_time = door_wait_time

    def initialize_device_factory(self, type=""):
        try:
            Device.pin_factory = LGPIOFactory()
        except PinUnknownPi:
            Device.pin_factory = MockFactory(
                pin_class=MockPWMPin if type == "PWM" else None
            )

    def closed(self):
        with self.lock:
            self.state = DoorState.CLOSED

    def opened(self):
        with self.lock:
            self.state = DoorState.OPEN

    def up(self):
        with self.lock:
            self.state = DoorState.OPENING
            self.motor.forward()
            self.upper_stop_sensor.wait_for_active(self.door_wait_time)
            self.motor.stop()

    def down(self):
        with self.lock:
            self.state = DoorState.CLOSING
            self.motor.backward()
            self.upper_stop_sensor.wait_for_active(self.door_wait_time)
            self.motor.stop()
