
from machine import Pin, reset
from neopixel import NeoPixel
import time
import network
import json
import socket
import ntptime
from webpage import html


np = NeoPixel(Pin(48, Pin.OUT), 1)
n = 1


def reboot():
    time.sleep(10)
    reset()


def startup(startup_color):
    np[0] = (0, 0, 0)
    np.write()

    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)

            factor = val / 255
            np[j] = (
                int(startup_color[0] * factor),
                int(startup_color[1] * factor),
                int(startup_color[2] * factor),
            )
        np.write()
        time.sleep_ms(5)
    turn_off_neopixel()
    return


def turn_off_neopixel():
    print("Turn off neopixel")
    np[0] = (0, 0, 0)
    np.write()
    return


def start_ap(settings):
    print("Start AP mode")

    wifi_settings = settings.get("wifi", {})

    ssid = wifi_settings.get("AP_SSID")
    password = wifi_settings.get("AP_PSWD")

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    ap.config(
        essid=ssid,
        password=password,
        authmode=network.AUTH_WPA_WPA2_PSK
    )

    print("AP mode active")
    print("IP:", ap.ifconfig()[0])

    return ap


def connect_wifi(settings):
    wifi_settings = settings.get("wifi", {})

    ssid = wifi_settings.get("SSID")
    password = wifi_settings.get("PSWD")

    # No wifi configured
    if not ssid or not password:
        print("Wifi not configured")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("connected to wifi")

    if not wlan.isconnected():
        wlan.connect(ssid, password)

        # Try to connect for 10 seconds
        for _ in range(20):
            if wlan.isconnected():
                break

            print("Connecting to wifi")
            time.sleep(0.5)

    if wlan.isconnected():
        print("Connected to wifi")
        print("Wifi ifconfig:", wlan.ifconfig())
        return True

    print("Connecting to wifi failed")
    wlan.disconnect()
    return False


def web_page():
    return html


def return_data(bme):
    temp = bme.temperature
    hum = bme.humidity
    pres = bme.pressure
    data = {
        "temperature": temp,
        "humidity": hum,
        "pressure": pres
    }

    body = json.dumps(data)

    return (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Connection: close\r\n"
        "\r\n"
        + body
    )


def process_wifi(request):
    try:
        # Read settings
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print("Problem reading settings: ", e)

        headers, body = request.split("\r\n\r\n", 1)

        data = json.loads(body)

        ssid = data.get("ssid")
        password = data.get("password")
        print(ssid)
        print(password)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        wlan.connect(ssid, password)

        # Wait for 10seconds max
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(0.5)

        if wlan.isconnected():
            print("Successfully connected")
            ip = wlan.ifconfig()[0]

            # Save if connected successfully
            settings["wifi"]["SSID"] = ssid
            settings["wifi"]["PSWD"] = password

            with open("settings.json", "w") as f:
                json.dump(settings, f)
            print("return data")
            return (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Connection: close\r\n"
                "\r\n"
                + json.dumps({
                    "success": True,
                    "ip": ip
                }), True
            )

        return (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps({
                "success": False,
                "ip": None
            }), False
        )

    except Exception as e:
        print("WiFi error:", e)


def process_email(request):

    try:

        host = "192.168.0.126"
        port = 8080
        addr = socket.getaddrinfo(
            host,
            port,
            0,
            socket.SOCK_STREAM
        )[0][-1]

        # Read settings
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print("Problem reading settings: ", e)

        headers, body = request.split("\r\n\r\n", 1)

        data = json.loads(body)

        email = data.get("email")
        terrarium_name = data.get("terrarium_name")
        terrarium_id = settings.get("device_id")

        s = socket.socket()
        s.connect(addr)

        backend_body = json.dumps(
            {
                "email": email,
                "terrariumName": terrarium_name,
                "terrariumId": terrarium_id
            }
        )

        backend_request = (
            "POST /terrariums/link HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "{}"
        ).format(
            host,
            len(backend_body),
            backend_body
        )

        s.sendall(backend_request.encode())

        response = s.recv(1024)

        print("Backend response:", response.decode())

        s.close()

        return (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps({
                "success": True
            }), True
        )

    except Exception as e:
        # print("WiFi error:", e)
        return (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps({
                "success": False
            }), False
        )


def check_and_save_apikey():
    try:
        host = "192.168.0.126"
        port = 8080

        # Read settings
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print("Problem reading settings: ", e)

        # Stop this function if we have an API key in settings.json
        if settings.get("api_key"):
            return True

        device_id = settings.get("device_id")

        if not device_id:
            print("No device_id configured")
            return False

        addr = socket.getaddrinfo(
            host,
            port,
            0,
            socket.SOCK_STREAM
        )[0][-1]

        s = socket.socket()
        s.connect(addr)

        request = (
            "GET /terrariums/link/{} HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(
            device_id,
            host
        )

        s.sendall(request.encode())

        response = b""

        while True:
            chunk = s.recv(1024)

            if not chunk:
                break

            response += chunk

        s.close()

        response_text = response.decode()

        print("Backend response:")
        print(response_text)

        headers, body = response_text.split("\r\n\r\n", 1)

        # Check whether spring uses chunked encoding (weird 42 and stuff i kinda don't get it)
        if "Transfer-Encoding: chunked" in headers:

            decoded_body = ""

            while body:
                # First line should be size of chunk in hex
                chunk_size_str, body = body.split("\r\n", 1)

                chunk_size = int(chunk_size_str, 16)

                # 0 = end of message
                if chunk_size == 0:
                    break

                # ACTUALLY read the json data
                decoded_body += body[:chunk_size]

                # Remove chunk + CRLF
                body = body[chunk_size + 2:]

            body = decoded_body

        print("Decoded body:", body)

        data = json.loads(body)

        print("Connection data:", data)

        status = data.get("status")
        api_key = data.get("APIKey")

        # Only save is the status is accepted (there is no api key when not accepted)
        if status == "ACCEPTED" and api_key:

            settings["api_key"] = api_key

            with open("settings.json", "w") as f:
                json.dump(settings, f)

            print("API key saved successfully!")
            return True

        print("Terrarium not accepted yet:", status)
        return False

    except Exception as e:
        print("Connection check error:", e)
        return False


def send_sensor_data(bme):
    try:
        host = "192.168.0.126"
        port = 8080

        # Read settings
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print("Problem reading settings: ", e)

        device_id = settings.get("device_id")
        api_key = settings.get("api_key")

        if not api_key:
            print("No API key yet")
            return False

        raw_temperature = bme.temperature
        raw_humidity = bme.humidity

        # BME280 gives '25.86C' and '43.22%' instead of just float so for the backend we need to fix that
        temperature = float(raw_temperature.replace("C", "").strip())
        humidity = float(raw_humidity.replace("%", "").strip())

        # Create JSON body for sending the data
        body = json.dumps({
            "temperature": temperature,
            "Humidity": humidity
        })

        addr = socket.getaddrinfo(
            host,
            port,
            0,
            socket.SOCK_STREAM
        )[0][-1]

        s = socket.socket()
        s.connect(addr)

        request = (
            "POST /terrariums/data/{} HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Content-Type: application/json\r\n"
            "X-API-Key: {}\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "{}"
        ).format(
            device_id,
            host,
            api_key,
            len(body),
            body
        )

        s.sendall(request.encode())

        response = b""

        while True:
            chunk = s.recv(1024)

            if not chunk:
                break

            response += chunk

        s.close()

        # Good for testing but in comment to increase performance
        # print("Backend response:")
        # print(response.decode())

        return True

    except Exception as e:
        print("Sensor data error:", e)
        return False


def get_settings():
    try:
        # Read settings
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print("Problem reading settings: ", e)

        data = {
            "day": settings.get("day", {}),
            "night": settings.get("night", {}),
            "feeder": settings.get("feeder", {})
        }

        return (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps(data)
        )

    except Exception as e:
        return (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps({
                "success": False
            })
        )


def process_settings(request):
    try:
        print("Changing settings")
        headers, body = request.split("\r\n\r\n", 1)

        new_settings = json.loads(body)

        # Read settings
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print("Problem reading settings: ", e)

        settings["day"] = {
            "start_time": new_settings.get("day", {}).get("start_time"),
            "temp": new_settings.get("day", {}).get("temp"),
            "temp_margin": new_settings.get("day", {}).get("temp_margin"),
            "temp_too_high_margin": new_settings.get("day", {}).get(
                "temp_too_high_margin"
            ),
            "humidity": new_settings.get("day", {}).get("humidity"),
            "humidity_margin": new_settings.get("day", {}).get("humidity_margin")
        }

        settings["night"] = {
            "start_time": new_settings.get("night", {}).get("start_time"),
            "temp": new_settings.get("night", {}).get("temp"),
            "temp_margin": new_settings.get("night", {}).get("temp_margin"),
            "temp_too_high_margin": new_settings.get("night", {}).get(
                "temp_too_high_margin"
            ),
            "humidity": new_settings.get("night", {}).get("humidity"),
            "humidity_margin": new_settings.get("night", {}).get("humidity_margin")
        }

        settings["feeder"] = {
            "days": new_settings.get("feeder", {}).get("days"),
            "time_first_portion": new_settings.get("feeder", {}).get(
                "time_first_portion"
            ),
            "time_second_portion": new_settings.get("feeder", {}).get(
                "time_second_portion"
            )
        }

        # Save settings
        with open("settings.json", "w") as f:
            json.dump(settings, f)
            print("Settings saved")

        return (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps({
                "success": True,
                "message": "Settings saved"
            }),
            True
        )

    except Exception as e:
        print("Settings error:", e)

        return (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
            + json.dumps({
                "success": False,
                "message": str(e)
            }),
            False
        )


def get_day_night(settings):
    current_hour = time.localtime()[3]

    # Belgium is UTC + 2
    current_hour += 2
    print(current_hour)

    day_start = settings.get("day", {}).get("start_time")
    night_start = settings.get("night", {}).get("start_time")

    if day_start <= current_hour < night_start:
        print("day")
        return "day"
    print("night")

    return "night"


def control_heater(temperature, settings, heater):
    target = settings.get(get_day_night(settings), {}).get("temp")
    margin = settings.get(get_day_night(settings), {}).get("temp_margin")

    if temperature <= target - margin:
        heater.duty_u16(65535)
        print("Heaterpad ON")

    elif temperature >= target:
        heater.duty_u16(0)
        print("Heaterpad OFF")


def control_cooling(temperature, settings, fan1, fan2):
    target = settings.get(get_day_night(settings), {}).get("temp")
    too_high_margin = settings.get(
        get_day_night(settings), {}).get("temp_too_high_margin")

    if temperature >= target + too_high_margin:
        fan1.duty_u16(65535)
        fan2.duty_u16(65535)

        print("Coolingfans ON")

    else:
        fan1.duty_u16(0)
        fan2.duty_u16(0)

        print("Coolingfans OFF")


def control_humidity(humidity, settings, mister):
    target = settings.get(get_day_night(settings), {}).get("humidity")
    margin = settings.get(get_day_night(settings), {}).get("humidity_margin")

    if humidity <= target - margin:
        mister.duty_u16(65535)
        print("Mister ON")

    elif humidity >= target:
        mister.duty_u16(0)
        print("Mister OFF")


def control_feeder(settings, feeder_motor):
    current_time = time.localtime()

    current_day = current_time[6]
    current_hour = current_time[3]

    feeder_days = settings.get("feeder", {}).get("days", [])
    time_first_portion = settings.get("feeder", {}).get("time_first_portion")
    time_second_portion = settings.get("feeder", {}).get("time_second_portion")

    # Only open feeder on days that are defined in the settings
    if current_day not in feeder_days:
        return

    # Give first portion (open to 90°)
    if current_hour == time_first_portion:
        feeder_motor.move(90)

    # Give second portion (open to 180°)
    elif current_hour == time_second_portion:
        feeder_motor.move(180)


def control_lighting(settings, pin_led, pin_relai_lamp):
    if (get_day_night(settings) == "day"):
        pin_led.duty_u16(65535)
        pin_relai_lamp.value(1)
    else:
        pin_led.duty_u16(0)
        pin_relai_lamp.value(0)


def sync_time():
    try:
        print("Synchronizing time...")
        ntptime.settime()

        current_time = time.time()
        time.localtime(current_time)

        print("Time synchronized:", time.localtime())

    except Exception as e:
        print("Time sync error:", e)
