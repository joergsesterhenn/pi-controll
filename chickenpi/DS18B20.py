import time


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
