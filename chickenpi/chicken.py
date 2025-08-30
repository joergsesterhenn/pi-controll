import logging
import chickenpi.logging.logging  # noqa: F401
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from chickenpi.auth.auth import FirebaseUser, init_auth, lifespan, verify_firebase_token
from chickenpi.door.door import close_door, coop_door_state, open_door
from chickenpi.images.images import get_latest_image, get_new_image
from chickenpi.lights.lights import state, toggle
from chickenpi.temperature.temperature import get_readings

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

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


@app.exception_handler(HTTPException)
async def log_http_exception(request: Request, exc: HTTPException):
    logger.warning("HTTP %s on %s: %s", exc.status_code, request.url.path, exc.detail)
    raw = request.headers.get("Authorization")

    # Mask or trim it if you worry about logging secrets
    display = raw if not raw else f"{raw[:100]}…"

    logger.error(
        "Auth error (%s %s): %s – Authorization header: %s",
        request.method,
        request.url.path,
        exc.detail,
        display,
    )

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# 5. Optional: request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("← %s %s %s", request.method, request.url.path, response.status_code)
    return response


app.mount("/captures", StaticFiles(directory="."), name="captures")


@app.post("/door")
def coop_door(direction: str, user_info: FirebaseUser = Depends(verify_firebase_token)):
    logger.info("door sent %s by %s", direction, user_info.name)
    if direction == "up":
        return open_door()
    if direction == "down":
        return close_door()


@app.get("/door-state")
def door_state():
    # logger.info("door state requested by %s", user_info.name)
    logger.info("door-state")
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
