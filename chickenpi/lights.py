import logging
from gpiozero import OutputDevice, Device
from gpiozero.pins.lgpio import LGPIOFactory
from threading import Lock
from lgpio import gpiochip_open, gpio_read, gpiochip_close

logger = logging.getLogger(__name__)

lights_lock = Lock()

Device.pin_factory = LGPIOFactory()

# Delay creation of relay1 until first use
_relay1 = None

def get_relay():
    global _relay1
    if _relay1 is None:
        # Read the current GPIO state to avoid unexpected toggling
        chip0 = gpiochip_open(0)  # Usually /dev/gpiochip0
        current = gpio_read(chip0, 18)
        gpiochip_close(chip0)

        # Match the current state to avoid changing anything
        # If active_low: ON == 0, OFF == 1
        initial_value = False if current else True

        logger.info(f"Initializing relay1 on GPIO18 with initial_value={initial_value}")
        _relay1 = OutputDevice(18, active_high=False, initial_value=initial_value)
    return _relay1

def toggle():
    with lights_lock:
        relay = get_relay()
        state_before = relay.value
        relay.toggle()
        state_after = relay.value
        return {
            "status": "relay 1 toggled",
            "initial_state": state_before,
            "final_state": state_after,
        }

def state():
    with lights_lock:
        relay = get_relay()
        return {"on": relay.value == 1}

