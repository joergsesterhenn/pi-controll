import cv2
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Globales Kamera-Objekt, das über die lifespan gestartet wird
camera: Optional[cv2.VideoCapture] = None

def start_camera():
    """Initialisiert die USB-Kamera beim Serverstart."""
    global camera
    camera = cv2.VideoCapture(0)
    # Auflösungs-Kompromiss für gute Qualität & flüssigen Stream auf dem Pi 3
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    logger.info("USB Camera successfully initialized.")

def stop_camera():
    """Gibt die Kameraressourcen beim Server-Shutdown frei."""
    global camera
    if camera is not None:
        camera.release()
        logger.info("Camera resources released.")

def gen_frames():
    """Generator, der MJPEG-Frames von der Kamera liest."""
    global camera
    if camera is None or not camera.isOpened():
        logger.error("Camera is not initialized or closed.")
        return

    while True:
        success, frame = camera.read()
        if not success:
            logger.warning("Failed to read frame from camera.")
            break
        
        # Zu JPEG komprimieren (80% Qualität schont die Pi 3 CPU & Bandbreite)
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        # MJPEG-Format Multipart-Chunks für den Browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # 0.04s Sleep begrenzt den Stream auf ~25 FPS und verhindert 100% CPU-Last auf dem Pi 3
        time.sleep(0.04)
