"""
from threading import Thread
from CRS import CRS
from CVS import CVS
"""
import serial
from serial.serialutil import SerialTimeoutException
from time import sleep
from datetime import datetime, timedelta

def main():
    port = serial.Serial(port='/dev/serial1',
                         write_timeout=1,
                         timeout=1)
    try:
        port.write(b'1')
    except SerialTimeoutException:
        print("Written.")
    read = port.read()
    print(read)
"""
    print(port.BAUDRATES)
    
    for baudrate in port.BAUDRATES:
        print(baudrate)
        if 300 <= baudrate <= 150000:
            port.baudrate = baudrate
"""
"""            if read == b'Hello World!':
                print("Success")
    print("Done.")
"""    
if __name__ == '__main__':
    main()
    
