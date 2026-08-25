
from machine import Pin, reset
from neopixel import NeoPixel
import time
import network
import json
import socket


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
    html = """
    <!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Terrarium</title>
  </head>

  <body>
    <div id="data">
      <h1>Live data</h1>
      <p>Temperature: <span id="temperature">-</span></p>
      <p>Humidity: <span id="humidity">-</span></p>
      <p>Pressure: <span id="pressure">-</span></p>
    </div>

    <div id="connect_wifi">
      <h1>Connect to WiFi</h1>

      <form id="wifiForm">
        <label for="ssid">WiFi SSID</label><br />
        <input type="text" id="ssid" name="ssid" /><br />

        <label for="password">Password</label><br />
        <input type="password" id="password" name="password" /><br />

        <button type="submit">Connect</button>
      </form>
    </div>

    <div id="connect_email">
      <h1>Connect device to account</h1>

      <form id="emailForm">
        <label for="terrarium_name">Terrarium name</label><br />
        <input type="text" id="terrarium_name" name="terrarium_name" /><br />

        <label for="email">Email address</label><br />
        <input type="email" id="email" name="email" /><br />

        <button type="submit">Connect device</button><br />
      </form>
    </div>

    <script>
      const updateData = async () => {
        const response = await fetch("/data");
        const data = await response.json();

        document.getElementById("temperature").textContent = data.temperature;
        document.getElementById("humidity").textContent = data.humidity;
        document.getElementById("pressure").textContent = data.pressure;
      };

      const wifiForm = document.getElementById("wifiForm");

      wifiForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const ssid = document.getElementById("ssid").value;
        const password = document.getElementById("password").value;

        const response = await fetch("/wifi", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ssid: ssid,
            password: password,
          }),
        });
        const data = await response.json();

        data.success
          ? alert(
              `Connection successfull, you can connect through the new ip: ${data.ip}`,
            )
          : alert(`Connecting to wifi failed`);
      });

      const emailForm = document.getElementById("emailForm");

      emailForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const terrarium_name = document.getElementById("terrarium_name").value;

        const response = await fetch("/email", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            terrarium_name: terrarium_name,
          }),
        });

        const data = await response.json();

        alert(data.message);
      });

      updateData();
      setInterval(updateData, 10000);
    </script>
  </body>
</html>

    """
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
