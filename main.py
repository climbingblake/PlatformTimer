# Required Libraries
from machine import Pin, I2C
from time import ticks_ms, sleep_ms
import ssd1306  # if you have an OLED library; for LCD1602 via I2C, we use a different one.
import lcd_api
import i2c_lcd

# I2C LCD Setup
# On NodeMCU, typical pins for I2C are:
# D1 = GPIO5 (SCL)
# D2 = GPIO4 (SDA)
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
lcd = i2c_lcd.I2cLcd(i2c, 0x27, 2, 16)  # 0x27 is a common LCD I2C address

# Mechanical Switch Setup
# Connect one side of the switch to D5 (GPIO14)
# Connect the other side to GND
switch = Pin(14, Pin.IN, Pin.PULL_UP)  # PULL_UP ensures default HIGH when unpressed

# Variables
running = False
start_time = 0
idle_start_time = ticks_ms()


def format_time(ms):
    seconds = ms // 1000
    centiseconds = (ms % 1000) // 10  # two decimal places
    return "{:02d}.{:02d}".format(seconds, centiseconds)

# Main Loop
lcd.clear()
lcd.putstr("Timer Ready")
sleep_ms(1000)
lcd.clear()
lcd.putstr("Running:")
lcd.move_to(0, 1)
lcd.putstr("00.00")

while True:
    if switch.value() == 0:  # Switch pressed (circuit closed)
        if running:
            running = False
            idle_start_time = ticks_ms()
            lcd.move_to(0, 0)
            lcd.putstr("Stopped:     ")
            lcd.move_to(0, 1)
            lcd.putstr(format_time(ticks_ms() - start_time) + "   ")
        sleep_ms(200)  # debounce delay
    else:  # Switch held open
        if not running:
            running = True
            start_time = ticks_ms()  # reset to 0 every time it starts
            lcd.move_to(0, 0)
            lcd.putstr("Running:     ")

    if running:
        timer_ms = ticks_ms() - start_time
        lcd.move_to(0, 1)
        lcd.putstr(format_time(timer_ms))
    else:
        idle_ms = ticks_ms() - idle_start_time
        lcd.move_to(9, 1)
        lcd.putstr(format_time(idle_ms))

    sleep_ms(50)  # adjust refresh rate for stability
