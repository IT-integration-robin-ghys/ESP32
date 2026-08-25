import os
import json
import functions
import uuid


default_settings = {
    "device_id": "",  # start empty
    "startup_light_color": [255, 255, 255],  # Default white as color
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

# Generate UUID if device doesn't have one yet
if settings.get("device_id") == "":
    device_id = str(uuid.uuid4())
    settings["device_id"] = device_id

    with open("settings.json", "w") as f:
        json.dump(settings, f)

# Startup lighting effect
functions.startup_lighting(settings.get("startup_light_color", None))

# EXecute all files in files list
if len(files) > 1:
    print('The device have %d files' % len(files))
    for i in range(len(files)):
        if files[i] != 'boot.py':
            print('file name:', files[i])
            exec(open(files[i]).read(), globals())
else:
    print("MicroPython has no files!")
