
from machine import Pin
from neopixel import NeoPixel
import time

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
