import glob
import logging
import os
import subprocess
from datetime import datetime
from time import sleep
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from rich.pretty import pprint

from chickenpi.lights import toggle, state
from chickenpi.door import open_door, close_door, coop_door_state
from chickenpi.DS18B20 import DS18B20
import sys
from chickenpi.auth import verify_firebase_token
app = FastAPI()

origins = [
    "https://coop-pi.web.app",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://raspberrypi:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
logging.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# StreamHandler für die Konsole
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


app.mount("/captures", StaticFiles(directory="."), name="captures")

@app.post("/door")
def coop_door(direction:str, user_info: Annotated[dict, Depends(verify_firebase_token)]):
    if direction=="up":
        open_door()
    if direction=="down":
        close_door()

@app.get("/door-state", user_info: Annotated[dict, Depends(verify_firebase_token)])
def door_state():
    return coop_door_state()

@app.post("/lights", user_info: Annotated[dict, Depends(verify_firebase_token)])
def lights():
    return toggle()

@app.get("/light-state", user_info: Annotated[dict, Depends(verify_firebase_token)])
def light_state():
    return state()

@app.post("/capture", user_info: Annotated[dict, Depends(verify_firebase_token)])
def capture_image():
    foldername = f"captures/{datetime.now().strftime('%Y/%m/%d')}"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(foldername, exist_ok=True)
    filename = f"{foldername}/{timestamp}_capture.jpg"
    subprocess.run(["fswebcam", "-r", "1280x960", filename])
    return {"status": "image captured", "filename": filename}

@app.get("/temperature", user_info: Annotated[dict, Depends(verify_firebase_token)])
def read_temperature():
    # Map known sensor IDs to logical names
    sensor_map = {"28-0417a142c0ff": "inside", "28-0417a12507ff": "outside"}

    base_dir = "/sys/bus/w1/devices/"
    device_folders = glob.glob(base_dir + "28-*")

    readings = {}

    for folder in device_folders:
        sensor_id = folder.split("/")[-1]
        device_file = folder + "/w1_slave"
        label = sensor_map.get(sensor_id)

        if label:
            try:
                temp = DS18B20(device_file).read_temperature()
                readings[label] = round(temp, 1)
            except Exception as e:
                readings[label] = f"error: {e}"
    return readings


@app.get("/latest-image", user_info: Annotated[dict, Depends(verify_firebase_token)])
def latest_image():
    # Recursively find all *_capture.jpg files
    image_files = glob.glob("captures/20??/??/??/*_capture.jpg", recursive=True)
    if not image_files:
        return {"error": "No captures found"}

    image_files.sort(key=os.path.getmtime)
    latest = image_files[-1]
    return FileResponse(latest, media_type="image/jpeg")
