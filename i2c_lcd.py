# i2c_lcd.py
import time
from lcd_api import LcdApi
from machine import I2C

# Commands
LCD_CLR = 0x01
LCD_HOME = 0x02
LCD_ENTRY_MODE_SET = 0x04
LCD_DISPLAY_CONTROL = 0x08
LCD_FUNCTION_SET = 0x20
LCD_SET_DDRAM_ADDR = 0x80

# Flags for display entry mode
LCD_ENTRY_LEFT = 0x02
LCD_ENTRY_SHIFT_DECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAY_ON = 0x04
LCD_CURSOR_OFF = 0x00
LCD_BLINK_OFF = 0x00

# Flags for function set
LCD_4BIT_MODE = 0x00
LCD_2LINE = 0x08
LCD_5x8DOTS = 0x00

# Pin mapping
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = True
        self._current = 0
        self.init_lcd()

    def init_lcd(self):
        time.sleep_ms(50)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_us(100)
        self.hal_write_init_nibble(0x03)
        self.hal_write_init_nibble(0x02)

        self.write_cmd(LCD_FUNCTION_SET | LCD_2LINE | LCD_5x8DOTS | LCD_4BIT_MODE)
        self.write_cmd(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON)
        self.write_cmd(LCD_CLR)
        self.write_cmd(LCD_ENTRY_MODE_SET | LCD_ENTRY_LEFT | LCD_ENTRY_SHIFT_DECREMENT)
        self.backlight_on()

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << 4)
        self.hal_write_byte(byte)

    def hal_write_byte(self, byte):
        self.i2c.writeto(self.i2c_addr, bytes([byte | (self.backlight << SHIFT_BACKLIGHT)]))
        self.hal_toggle_enable(byte)

    def hal_toggle_enable(self, byte):
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E | (self.backlight << SHIFT_BACKLIGHT)]))
        time.sleep_us(500)
        self.i2c.writeto(self.i2c_addr, bytes([(byte & ~MASK_E) | (self.backlight << SHIFT_BACKLIGHT)]))
        time.sleep_us(500)

    def write_cmd(self, cmd):
        high = cmd & 0xF0
        low = (cmd << 4) & 0xF0
        self.hal_write(high)
        self.hal_write(low)

    def write_data(self, data):
        high = data & 0xF0
        low = (data << 4) & 0xF0
        self.hal_write(high, MASK_RS)
        self.hal_write(low, MASK_RS)

    def hal_write(self, data, mode=0):
        byte = data | mode
        self.hal_write_byte(byte)

    def _backlight_on(self):
        self.backlight = True
        self.i2c.writeto(self.i2c_addr, bytes([self.backlight << SHIFT_BACKLIGHT]))

    def _backlight_off(self):
        self.backlight = False
        self.i2c.writeto(self.i2c_addr, bytes([0]))
