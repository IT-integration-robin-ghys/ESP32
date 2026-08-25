
from machine import Pin
from neopixel import NeoPixel
import time
import network
import json


np = NeoPixel(Pin(48, Pin.OUT), 1)
n = 1


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

        await fetch("/wifi", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ssid: ssid,
            password: password,
          }),
        });
      });

      const emailForm = document.getElementById("emailForm");

      emailForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;

        await fetch("/email", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
          }),
        });
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