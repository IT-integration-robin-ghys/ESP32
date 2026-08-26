
import os
import json
import functions
from functions import connect_wifi, start_ap, send_settings, get_settings_from_backend, sync_time, reboot

default_settings = {
    "device_id": "",
    "api-key": "",
    "startup_light_color": [255, 255, 255],  # Default white as color
    "wifi": {
        "SSID": "",
        "PSWD": "",
        "AP_SSID": "Terrarium",
        "AP_PSWD": "terrarium1234"
    },
    "day": {
        "start_time": 8,
        "temp": 21.0,
        "temp_margin": 1.0,
        "temp_too_high_margin": 10.0,
        "humidity": 60.0,
        "humidity_margin": 5.0,
    },
    "night": {
        "start_time": 21,
        "temp": 18.0,
        "temp_margin": 1.0,
        "temp_too_high_margin": 10.0,
        "humidity": 60.0,
        "humidity_margin": 5.0
    },
    "feeder": {
        "days": [0, 3],
        "time_first_portion": 10,
        "time_second_portion": 18
    }

}

# Read all files
files = os.listdir()

# Create settings.json if it doesn't exist yet
if "settings.json" not in files:
    try:
        with open("settings.json", "w") as f:
            f.write(json.dumps(default_settings))
        print("settings.json created")
        files.append("settings.json")
    except Exception as e:
        print("Something went wrong while creating the settings file: "+e)

# Read settings.json
try:
    with open("settings.json", "r") as f:
        settings = json.load(f)
except Exception as e:
    print("Problem reading settings: ", e)

# Generate device ID if needed


def generate_device_id():
    random_bytes = os.urandom(16)

    return "{:02x}{:02x}{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *random_bytes
    )


if not settings.get("device_id"):
    settings["device_id"] = generate_device_id()

    with open("settings.json", "w") as f:
        json.dump(settings, f)

    print("Generated device ID:", settings["device_id"])

functions.startup(settings.get("startup_light_color", None))

# Try to connect, if it fails start ap mode
connected = connect_wifi(settings)
if not connected:
    start_ap(settings)
else:
    if not sync_time():
        reboot()


api_key = settings.get("api_key")

if api_key:
    if connected:
        send_settings()
        get_settings_from_backend()

if len(files) > 1:
    print('The device have %d files' % len(files))
    for i in range(len(files)):
        if files[i] != 'boot.py':
            print('file name:', files[i])
            exec(open(files[i]).read(), globals())
else:
    print("MicroPython has no files!")
