from machine import Pin, PWM, I2C
from servo import Servo
from time import sleep_ms
import BME280
from functions import web_page, return_data

try:
    import usocket as socket
except:
    import socket


def create_pwm(pin_number, frequency=1000, duty=32768):
    pwm = PWM(Pin(pin_number, Pin.OUT))
    pwm.freq(frequency)
    pwm.duty_u16(duty)
    return pwm


def set_duty(pwm, duty):
    pwm.duty_u16(duty)


feeder_motor = Servo(pin=9)
pwm10 = create_pwm(10, frequency=1000, duty=0)
pwm11 = create_pwm(11, frequency=1000, duty=0)
pwm12 = create_pwm(12, frequency=1000, duty=0)
pwm13 = create_pwm(13, frequency=1000, duty=0)
pwm14 = create_pwm(14, frequency=1000, duty=0)

i2c = I2C(
    0,
    sda=Pin(1),
    scl=Pin(2),
    freq=10000
)

# Webserver
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
s.setblocking(False)


while True:
    bme = BME280.BME280(i2c=i2c)

    # Look for the http requests
    try:
        conn, addr = s.accept()

        print('Got a connection from %s' % str(addr))

        request = conn.recv(1024).decode()
        print('Content = %s' % request)

        if "GET /data" in request:
            response = return_data(bme)
        elif "POST /wifi" in request:
            response = "/wifi"
        elif "POST /email" in request:
            response = "/email"
        else:
            #return web page if its a regular request
            response = web_page()

        conn.send(response)
        conn.close()

    except OSError:
        # Skip if no connections
        pass

    # don't need these for now
    # feeder_motor.move(0)

    # set_duty(pwm10, 65535)
    # set_duty(pwm11, 65535)
    # set_duty(pwm12, 65535)
    # set_duty(pwm13, 65535)
    # set_duty(pwm14, 65535)
    # sleep_ms(1000)
