import json

from machine import Pin, PWM, I2C
from servo import Servo
from time import sleep_ms
import BME280
from functions import web_page, return_data, process_wifi, process_email, reboot, check_and_save_apikey, send_sensor_data, control_heater, control_cooling, control_humidity, control_feeder, get_settings, process_settings, control_lighting, sync_time, get_settings_from_backend

try:
    import usocket as socket
except:
    import socket

try:
    with open("settings.json", "r") as f:
        settings = json.load(f)
except Exception as e:
    print("Problem reading settings: ", e)

api_key = settings.get("api_key")

# Webserver
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    s.setblocking(False)
except:
    reboot()


def create_pwm(pin_number, frequency=1000, duty=32768):
    pwm = PWM(Pin(pin_number, Pin.OUT))
    pwm.freq(frequency)
    pwm.duty_u16(duty)
    return pwm


if not sync_time():
    reboot()

feeder_motor = Servo(pin=9)
mist_pin = create_pwm(10, frequency=1000, duty=0)
M5_fan2 = create_pwm(11, frequency=1000, duty=0)
M4_fan1 = create_pwm(12, frequency=1000, duty=0)
M3_heating = create_pwm(13, frequency=1000, duty=0)
M2_led = create_pwm(14, frequency=1000, duty=0)

relai_lamp = Pin(21, Pin.OUT, value=0)

i2c = I2C(
    0,
    sda=Pin(1),
    scl=Pin(2),
    freq=10000
)

# Move servo to start position
feeder_motor.move(0)


# Flag for rebooting when wifi form is successfull
reboot_after_response = False
# Flag for if terrarium request has been sent to backend
terrarium_request_successfully_sent = False

bme = BME280.BME280(i2c=i2c)
timer_60s = 0


while True:
    temperature = float(bme.temperature.replace("C", ""))
    humidity = float(bme.humidity.replace("%", ""))

    control_heater(
        temperature,
        settings,
        M3_heating
    )

    control_cooling(
        temperature,
        settings,
        M4_fan1,
        M5_fan2
    )

    control_humidity(
        humidity,
        settings,
        mist_pin
    )

    control_feeder(
        settings,
        feeder_motor
    )

    control_lighting(
        settings,
        M2_led,
        relai_lamp

    )

    timer_60s += 1
    if timer_60s >= 120:
        timer_60s = 0

        if api_key:
            send_sensor_data(bme)
            get_settings_from_backend()

    sleep_ms(500)

    # Look for the http requests
    try:
        conn, addr = s.accept()

        print('Got a connection from %s' % str(addr))

        request = conn.recv(1024).decode()
        # print('Content = %s' % request)

        if "GET /data" in request:
            response = return_data(bme)
        elif "GET /settings" in request:
            response = get_settings()
        elif "POST /settings" in request:
            response, reboot_after_response = process_settings(request)
        elif "POST /wifi" in request:
            response, reboot_after_response = process_wifi(request)
        elif "POST /email" in request:
            if terrarium_request_successfully_sent:
                response = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Type: application/json\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    + json.dumps({
                        "success": False,
                        "message": "Terrarium request has already been sent"
                    })
                )
            else:
                response, terrarium_request_successfully_sent = process_email(
                    request)
        else:
            # return web page if its a regular request
            response = web_page()

        conn.sendall(response.encode())
        conn.close()

        if reboot_after_response:
            reboot()

        if terrarium_request_successfully_sent:
            check_and_save_apikey()

    except OSError:
        # Skip if no connections
        pass
