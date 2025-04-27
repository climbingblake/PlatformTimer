# i2c_scan.py
from machine import Pin, I2C
import time

# Adjust these pins if needed
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

print("Scanning I2C bus...")
devices = i2c.scan()

if devices:
    print("I2C devices found:", len(devices))
    for device in devices:
        print("Decimal address:", device, " | Hex address:", hex(device))
else:
    print("No I2C devices found")
