import os
import json

files = os.listdir()

default_settings = {
    "Test": 1
}

if "settings.json" not in files:
    try:
        with open("settings.json", "w") as f:
            f.write(json.dumps(default_settings))
        print("settings.json created")
        files.append("settings.json")
    except Exception as e:
        print("Something went wrong while creating the settings file: "+e)

if len(files) > 1:
    print('The device have %d files' % len(files))
    for i in range(len(files)):
        if files[i] != 'boot.py':
            print('file name:', files[i])
            exec(open(files[i]).read(), globals())
else:
    print("MicroPython has no files!")