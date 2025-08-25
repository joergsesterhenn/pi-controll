import glob
import time


def get_readings(base_dir="/sys/bus/w1/devices/"):
    # Map known sensor IDs to logical names
    sensor_map = {"28-0417a142c0ff": "inside", "28-0417a12507ff": "outside"}
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


class DS18B20:
    def __init__(self, device_file):
        self.device_file = device_file

    def read_raw(self):
        with open(self.device_file, "r") as f:
            return f.readlines()

    def read_temperature(self):
        lines = self.read_raw()
        while lines[0].strip()[-3:] != "YES":
            time.sleep(0.2)
            lines = self.read_raw()
        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2 :]
            return float(temp_string) / 1000.0
        else:
            raise ValueError("Could not parse temperature")
