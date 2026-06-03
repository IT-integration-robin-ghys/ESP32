from machine import Pin
from neopixel import NeoPixel
import time

np = NeoPixel(Pin(48, Pin.OUT), 1)
n = 1


def startup(startup_color):
    try:
        color = tuple(
            int(c) for c in startup_color) if startup_color is not None else (127, 0, 0)
    except Exception:
        color = (127, 0, 0)

    np[0] = color
    np.write()

    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()
        time.sleep_ms(5)
    return
