from gpiozero.exc import PinUnknownPi
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero.pins.mock import MockFactory, MockPWMPin


def get_device_factory(type=""):
    try:
        return LGPIOFactory()
    except PinUnknownPi:
        return MockFactory(pin_class=MockPWMPin if type == "PWM" else None)
