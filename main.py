from machine import Pin, PWM
from time import sleep_ms


def create_pwm(pin_number, frequency=1000, duty=32768):
    pwm = PWM(Pin(pin_number, Pin.OUT))
    pwm.freq(frequency)
    pwm.duty_u16(duty)
    return pwm


def set_duty(pwm, duty):
    pwm.duty_u16(duty)


pwm10 = create_pwm(10, frequency=1000, duty=0)
pwm11 = create_pwm(11, frequency=1000, duty=0)
pwm12 = create_pwm(12, frequency=1000, duty=0)
pwm13 = create_pwm(13, frequency=1000, duty=0)
pwm14 = create_pwm(14, frequency=1000, duty=0)


while True:
    set_duty(pwm10, 65535)
    set_duty(pwm11, 65535)
    set_duty(pwm12, 65535)
    set_duty(pwm13, 65535)
    set_duty(pwm14, 65535)
    sleep_ms(1000)
