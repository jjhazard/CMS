import board
import busio
import digitalio
import time
from lib.Test import Create
from time import sleep
import adafruit_rfm69
from time import sleep
def main():
    # RFM69 Configuration
    CS = digitalio.DigitalInOut(board.CE1)
    RESET = digitalio.DigitalInOut(board.D25)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
    try:
        while True:
            rfm69.send(b'Hello')
            print("sent Hello")
            sleep(5)
    except KeyboardInterrupt:
        pass
    """
    for i in range(5):
        Create('/home/pi/CMS/CRSCodes/available',
               '/home/pi/CMS/CRSCodes/Dispatched/',
               '/home/pi/CMS/CRSCodes/Expired/').execute()
        Create('/home/pi/CMS/CVSCodes/available',
               '/home/pi/CMS/CVSCodes/Dispatched/',
               '/home/pi/CMS/CVSCodes/Expired/').execute()
    """

if __name__ == '__main__':
    main()
    
