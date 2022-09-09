
"""
Wiring Check, Pi Radio w/RFM9x

Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
Author: Brent Rubell for Adafruit Industries
"""
import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import the RFM9x radio module.
import adafruit_rfm9x


# Configure RFM9x LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

try:
    while True:
        # Attempt to set up the RFM9x Module
        try:
            rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
        except RuntimeError as error:
            # Thrown on version mismatch
            print('RFM9x Error: ', error)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
