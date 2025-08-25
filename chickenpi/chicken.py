import logging
import sys
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from chickenpi.images import get_latest_image, get_new_image
from chickenpi.lights import toggle, state
from chickenpi.door import open_door, close_door, coop_door_state
from chickenpi.auth import verify_firebase_token
from chickenpi.temperature import get_readings

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
    return get_readings()


@app.get("/latest-image")
def latest_image(user_info: Annotated[dict, Depends(verify_firebase_token)]):
    latest_image = get_latest_image()
    return FileResponse(latest_image, media_type="image/jpeg")
