from datetime import datetime
import glob
import os
import subprocess


def get_latest_image(directory="captures"):
    image_files = glob.glob(f"{directory}/20??/??/??/*_capture.jpg", recursive=True)
    if not image_files:
        return ""
    image_files.sort(key=os.path.getmtime)
    latest_image = image_files[-1]
    return latest_image


def get_new_image(directory="captures"):
    foldername = f"{directory}/{datetime.now().strftime('%Y/%m/%d')}"
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(foldername, exist_ok=True)
    filename = f"{foldername}/{timestamp}_capture.jpg"
    subprocess.run(["fswebcam", "-r", "1280x960", filename])
    return filename
