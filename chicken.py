import os
from datetime import datetime
from gpiozero import Motor, OutputDevice
from time import sleep
from rich.pretty import pprint
import subprocess
import glob

from DS18B20 import DS18B20

def capture_image():
    foldername = datetime.now().strftime("%Y/%m/%d")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(foldername, exist_ok=True)
    filename = f"{foldername}/{timestamp}_capture.jpg"
    subprocess.run(["fswebcam", "-r", "1024x768", filename])



def coop_door():
    # Set up the motor with GPIOs for IN_A and IN_B and EN_A
    # GPIO 17 = pin 11, GPIO 27 = pin 13, GPIO 22 = pin 15
    motor = Motor(forward=24, backward=27, enable=23)
    motor.forward()
    print("go")
    sleep(3)
    motor.stop()
    sleep(1)
    print("back")
    motor.backward()
    sleep(3)
    motor.stop()
    print("stop")


def lights():
    # only use "green" pins 4, 17, 18, 27 since those are "low" per default do not use uart pins
    # GPIO 4 = pin 7
    # power relay separately with 5 V and logic with 3 V
    relay1 = OutputDevice(17, active_high=False, initial_value=False)
    pprint(relay1)
    relay1.toggle()
    pprint(relay1)
    sleep(10)
    relay1.toggle()
    pprint(relay1)


def temp():
    """
    Prerequisites:
    --------------
    Enable 1-Wire via raspi-config or by adding this line to /boot/config.txt:

        dtoverlay=w1-gpio

    Reboot, then check for the sensor under:

        /sys/bus/w1/devices/

    You should see a directory like:

        28-00000xxxxxxx.
    """
    base_dir = '/sys/bus/w1/devices/'
    device_folders = glob.glob(base_dir + '28-*')
    pprint(device_folders)
    sensors = []
    for folder in device_folders:
        device_file = folder + '/w1_slave'
        sensors.append((folder.split('/')[-1], DS18B20(device_file)))

    # Read and print temperature from each sensor
    for sensor_id, sensor in sensors:
        try:
            temp = sensor.read_temperature()
            print(f"Sensor {sensor_id}: {temp:.2f} °C")
        except Exception as e:
            print(f"Sensor {sensor_id} error: {e}")
