
import os
import json
import functions


default_settings = {
    "device_id": "",
    "startup_light_color": [255, 255, 255],  # Default white as color
    "wifi": {
        "SSID": "",
        "PSWD": ""
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

if len(files) > 1:
    print('The device have %d files' % len(files))
    for i in range(len(files)):
        if files[i] != 'boot.py':
            print('file name:', files[i])
            exec(open(files[i]).read(), globals())
else:
    print("MicroPython has no files!")
