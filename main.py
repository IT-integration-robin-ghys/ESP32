

from machine import Pin, PWM, I2C
from servo import Servo
from time import sleep_ms
import BME280


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


while True:
    feeder_motor.move(0)
    sleep_ms(1000)
    feeder_motor.move(180)
    set_duty(pwm10, 65535)
    set_duty(pwm11, 65535)
    set_duty(pwm12, 65535)
    set_duty(pwm13, 65535)
    set_duty(pwm14, 65535)

    bme = BME280.BME280(i2c=i2c)
    temp = bme.temperature
    hum = bme.humidity
    pres = bme.pressure
    # uncomment for temperature in Fahrenheit
    # temp = (bme.read_temperature()/100) * (9/5) + 32
    # temp = str(round(temp, 2)) + 'F'
    print('Temperature: ', temp)
    print('Humidity: ', hum)
    print('Pressure: ', pres)

    sleep_ms(1000)
