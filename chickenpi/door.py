import logging
from gpiozero import Motor, DigitalInputDevice, Device
from gpiozero.pins.lgpio import LGPIOFactory
from threading import Lock
from enum import Enum

logger = logging.getLogger(__name__)

class Doorstate(Enum):
    UNDEFINED, OPEN, CLOSED, OPENING, CLOSING = range(5)

door_state = Doorstate.UNDEFINED

door_lock = Lock()

Device.pin_factory = LGPIOFactory()
motor = Motor(forward=17, backward=22, enable=23)
upper_stop_sensor = DigitalInputDevice(pin=6, pull_up=False)
lower_stop_sensor = DigitalInputDevice(pin=19, pull_up=False)

def _on_close():
    global door_state
    with door_lock:
        door_state=Doorstate.CLOSED

lower_stop_sensor.when_activated = _on_close

def _on_open():
    global door_state
    with door_lock:
        door_state=Doorstate.OPEN

upper_stop_sensor.when_activated = _on_open

def open_door():
    global door_state
    with door_lock:
        if door_state == Doorstate.OPENING:
            logger.info("door is already opening")
            return {"status": "door opening"}

        if door_state == Doorstate.OPEN:
            logger.info("door is already open")
            return {"status": "door open"}

        door_state = Doorstate.OPENING
        logger.info("opening door")
        motor.forward()
        upper_stop_sensor.wait_for_active(10)
        motor.stop()
        door_state = Doorstate.OPEN
        return {"status": "door open"}


def coop_door_state():
    with door_lock:
        if door_state != Doorstate.UNDEFINED:
            if upper_stop_sensor.value:
                return {"status": Doorstate.OPEN.value}
            if lower_stop_sensor.value:
                return {"status": Doorstate.CLOSED.value}
        else:
            return {"status": door_state.value}



def close_door():
    global door_state
    with door_lock:
        if door_state == Doorstate.CLOSING:
            logger.info("door is already closing")
            return {"status": "door closing"}

        if door_state == Doorstate.CLOSED:
            logger.info("door is already closed")
            return {"status": "door closed"}

        door_state = Doorstate.CLOSING
        logger.info("closing door")
        motor.backward()
        lower_stop_sensor.wait_for_active(10)
        motor.stop()
        door_state = Doorstate.CLOSED
        return {"status": "door closed"}

