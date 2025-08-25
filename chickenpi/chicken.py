import glob
import logging
import os
import sys
import subprocess
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from chickenpi.images import get_latest_image, get_new_image
from chickenpi.lights import toggle, state
from chickenpi.door import open_door, close_door, coop_door_state
from chickenpi.DS18B20 import DS18B20
from chickenpi.auth import verify_firebase_token

app = FastAPI()

origins = [
    "https://coop-pi.web.app",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://raspberrypi:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# StreamHandler für die Konsole
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


app.mount("/captures", StaticFiles(directory="."), name="captures")


@app.post("/door")
def coop_door(
    direction: str, user_info: Annotated[dict, Depends(verify_firebase_token)]
):
    if direction == "up":
        return open_door()
    if direction == "down":
        return close_door()


@app.get("/door-state")
def door_state(user_info: Annotated[dict, Depends(verify_firebase_token)]):
    return coop_door_state()


@app.post("/lights")
def lights(user_info: Annotated[dict, Depends(verify_firebase_token)]):
    return toggle()


@app.get("/light-state")
def light_state(user_info: Annotated[dict, Depends(verify_firebase_token)]):
    return state()


@app.post("/capture")
def capture_image(user_info: Annotated[dict, Depends(verify_firebase_token)]):
    filename = get_new_image()
    return {"status": "image captured", "filename": filename}


@app.get("/temperature")
def read_temperature(user_info: Annotated[dict, Depends(verify_firebase_token)]):
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


@app.get("/latest-image")
def latest_image(user_info: Annotated[dict, Depends(verify_firebase_token)]):
    latest_image = get_latest_image()
    return FileResponse(latest_image, media_type="image/jpeg")
