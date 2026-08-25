
from machine import Pin
from neopixel import NeoPixel
import time
import network


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
