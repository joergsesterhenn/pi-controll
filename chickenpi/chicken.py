import logging
import base64
import chickenpi.logging.logging  # noqa: F401


from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse 
from fastapi.staticfiles import StaticFiles

from chickenpi.auth.auth import (
    init_auth,
    FirebaseUser,
    verify_firebase_token,
    verify_firebase_token_from_query,
)
from chickenpi.door.door import close_door, open_door, coop_door_state
from chickenpi.door.door_driver import Door
from chickenpi.image.image import ImageStatus, get_latest_image, get_new_image
from chickenpi.light.light import toggle, state
from chickenpi.light.light_driver import Light
from chickenpi.temperature.temperature import Temperature, get_readings
from chickenpi.stream.stream import start_camera, stop_camera, gen_frames
from contextlib import asynccontextmanager
import sentry_sdk

sentry_sdk.init(
    dsn="https://b93f102ceabbff8abc772ffa927e989a@o4509977674711040.ingest.de.sentry.io/4509977744048208",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Enable logs to be sent to Sentry
    enable_logs=True,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    try:
        init_auth()
        logger.info("Firebase Admin initialized successfully.")
        start_camera()
    except Exception:
        logger.exception("Failed to initialize Firebase Admin:")
        raise

    yield  # === app is now running ===

    # --- Shutdown (optional) ---
    logger.info("Shutting down application.")
    stop_camera()

app = FastAPI(lifespan=lifespan)

origins = [
    "https://coop-pi.web.app",
    "http://localhost:8000",
    "http://localhost:8000/",
    "http://localhost:5173/",
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

    display = raw if not raw else f"{raw[:100]}…"

    logger.error(
        "HTTP error (%s %s): %s – Authorization header: %s",
        request.method,
        request.url.path,
        exc.detail,
        display,
    )

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.debug("← %s %s %s", request.method, request.url.path, response.status_code)
    return response


app.mount("/captures", StaticFiles(directory="."), name="captures")


@app.post("/door")
def coop_door(
    direction: str, user_info: FirebaseUser = Depends(verify_firebase_token)
) -> Door:
    logger.info("door sent %s by %s", direction, user_info.name)
    if direction == "up":
        return Door(status=open_door())
    if direction == "down":
        return Door(status=close_door())
    raise HTTPException(status_code=400, detail="Bad Request")


@app.get("/door/state")
def door_state(user_info: FirebaseUser = Depends(verify_firebase_token)) -> Door:
    logger.info("door-state requested by %s", user_info.name)
    return Door(status=coop_door_state())


@app.post("/light")
def lights(user_info: FirebaseUser = Depends(verify_firebase_token)) -> Light:
    logger.info("lights toggled by %s", user_info.name)
    return Light(status=toggle())


@app.get("/light/state")
def light_state(user_info: FirebaseUser = Depends(verify_firebase_token)) -> Light:
    logger.info("light state requested by %s", user_info.name)
    return Light(status=state())


@app.post("/image")
def capture_image(
    user_info: FirebaseUser = Depends(verify_firebase_token),
) -> ImageStatus:
    logger.info("new image requested by %s", user_info.name)
    filename = get_new_image()
    if not filename:
        raise HTTPException(status_code=404, detail="No image available")
    return ImageStatus(status="image captured", filename=filename)


@app.get("/image")
def latest_image(
    user_info: FirebaseUser = Depends(verify_firebase_token),
) -> dict:
    logger.info("latest image requested by %s", user_info.name)

    latest_image_path = get_latest_image()
    if not latest_image_path:
        raise HTTPException(status_code=404, detail="No image available")

    try:
        with open(latest_image_path, "rb") as image_file:
            binary_data = image_file.read()

        base64_encoded = base64.b64encode(binary_data).decode("utf-8")

        return {
            "status": "success",
            "image": base64_encoded,
            "media_type": "image/jpeg",
        }

    except Exception as e:
        logger.error("Failed to encode image: %s", str(e))
        raise HTTPException(status_code=500, detail="Error processing image file")


@app.get("/temperature")
def read_temperature(
    user_info: FirebaseUser = Depends(verify_firebase_token),
) -> Temperature:
    logger.info("temperature requested by %s", user_info.name)
    try:
        return get_readings()
    except Exception:
        raise HTTPException(status_code=500, detail="Could not read Temperature")

@app.get("/stream")
def video_stream(
    user_info: FirebaseUser = Depends(verify_firebase_token_from_query),
):
    """Gibt den kontinuierlichen Live-Stream (MJPEG) zurück."""
    logger.info("Live stream requested by %s (UID: %s)", user_info.name or "Unknown", user_info.uid)
    
    return StreamingResponse(
        gen_frames(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )