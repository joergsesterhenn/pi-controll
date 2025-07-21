from fastapi import FastAPI
from datetime import datetime
from gpiozero import Motor, OutputDevice
from time import sleep
import subprocess
import glob
from DS18B20 import DS18B20
from rich.pretty import pprint
import logging
import os
from fastapi.staticfiles import StaticFiles


logger=logging.getLogger(__name__)

app = FastAPI()
# Mount directory where images are saved (assuming same base directory)
app.mount("/captures", StaticFiles(directory="."), name="captures")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/capture")
def capture_image():
    foldername = f"captures/{datetime.now().strftime('%Y/%m/%d')}"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(foldername, exist_ok=True)
    filename = f"{foldername}/{timestamp}_capture.jpg"
    subprocess.run(["fswebcam", "-r", "1024x768", filename])
    return {"status": "image captured", "filename": filename}


@app.post("/door")
def coop_door():
    motor = Motor(forward=24, backward=27, enable=23)
    motor.forward()
    sleep(3)
    motor.stop()
    sleep(1)
    motor.backward()
    sleep(3)
    motor.stop()
    return {"status": "door cycled"}


@app.post("/lights")
def lights():
    relay1 = OutputDevice(17, active_high=False, initial_value=False)
    state_before = relay1.value
    relay1.toggle()
    sleep(10)
    relay1.toggle()
    state_after = relay1.value
    return {
        "status": "relay toggled twice",
        "initial_state": state_before,
        "final_state": state_after
    }


@app.get("/temperature")
def read_temperature():
    base_dir = '/sys/bus/w1/devices/'
    device_folders = glob.glob(base_dir + '28-*')
    results = []

    for folder in device_folders:
        device_file = folder + '/w1_slave'
        sensor_id = folder.split('/')[-1]
        sensor = DS18B20(device_file)
        try:
            temp = sensor.read_temperature()
            results.append({"sensor": sensor_id, "temperature": temp})
        except Exception as e:
            results.append({"sensor": sensor_id, "error": str(e)})

    return results

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def dashboard():
     logger.info("dashboard opened")
     with open("static/dashboard.html", "r", encoding="utf-8") as f:
        html = f.read()
        return html


@app.get("/latest-image")
def latest_image():
    # Recursively find all *_capture.jpg files
    image_files = glob.glob("captures/20??/??/??/*_capture.jpg", recursive=True)
    if not image_files:
        return {"error": "No captures found"}

    # Sort files by modification time (latest last)
    image_files.sort(key=os.path.getmtime)
    latest = image_files[-1]
    pprint({"url": f"/captures/{latest}"})
    return {"url": f"/captures/{latest}"}