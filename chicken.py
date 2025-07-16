from gpiozero import Motor, OutputDevice
from time import sleep
from rich.pretty import pprint


def coop_door():
    # Set up the motor with GPIOs for IN_A and IN_B and EN_A
    # GPIO 17 = pin 11, GPIO 27 = pin 13, GPIO 22 = pin 15
    motor = Motor(forward=17, backward=27, enable=22)
    motor.forward()
    print("go")
    sleep(3)
    motor.stop()
    sleep(1)
    motor.backward()
    sleep(3)
    motor.stop()
    print("stop")


def lights():
    # only use "green" pins 4, 17, 18, 27 since those are "low" per default do not use uart pins
    # GPIO 4 = pin 7
    # power relay separately with 5 V and logic with 3 V
    relay1 = OutputDevice(4, active_high=False, initial_value=False)
    pprint(relay1)
    relay1.toggle()
    pprint(relay1)
    sleep(10)
    relay1.toggle()
    pprint(relay1)

if __name__ == "__main__":
    #coop_door()
    lights()