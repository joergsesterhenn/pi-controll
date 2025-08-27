import logging
import sys

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from chickenpi.auth.auth import FirebaseUser, init_auth, verify_firebase_token
from chickenpi.door.door import close_door, coop_door_state, open_door
from chickenpi.images.images import get_latest_image, get_new_image
from chickenpi.lights.lights import state, toggle
from chickenpi.temperature.temperature import get_readings

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

init_auth()

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app.mount("/captures", StaticFiles(directory="."), name="captures")


@app.post("/door")
def coop_door(direction: str, user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("door sent %s by %s", direction, user_info.name)
    if direction == "up":
        return open_door()
    if direction == "down":
        return close_door()


@app.get("/door-state")
def door_state(user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("door state requested by %s", user_info.name)
    return coop_door_state()


@app.post("/lights")
def lights(user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("lights toggled by %s", user_info.name)
    return toggle()


@app.get("/light-state")
def light_state(user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("light state requested by %s", user_info.name)
    return state()


@app.post("/capture")
def capture_image(user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("new image requested by %s", user_info.name)
    filename = get_new_image()
    if not filename:
        return {"error": "No captures found"}
    return {"status": "image captured", "filename": filename}


@app.get("/temperature")
def read_temperature(user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("temperature requested by %s", user_info.name)
    return get_readings()


@app.get("/latest-image")
def latest_image(user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("latest image requested by %s", user_info.name)
    latest_image = get_latest_image()
    return FileResponse(latest_image, media_type="image/jpeg")
