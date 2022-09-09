"""
from threading import Thread
from CRS import CRS
from CVS import CVS
"""
import serial
from time import sleep
from datetime import datetime, timedelta
#from apscheduler.schedulers.background import BackgroundScheduler
import board
import digitalio
import busio
import adafruit_rfm9x
 
freq  = 915.0
cs    = digitalio.DigitalInOut(board.D12)
reset = digitalio.DigitalInOut(board.D16)
spi   = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, freq, baudrate=2000000)

def main():
    rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
    try:
        while True:
            packet = rfm9x.receive()
            if packet:
                print("Received: {0}".format(packet))
                packet_test = str(packet, "ascii")
                print("Received: {0}".format(packet_text))
                print("Singal strength: {0}".format(rfm9x.rssi))

    except KeyboardInterrupt:
        pass
    """
    #day='*', hour='*', minute='*', 
    sched = BackgroundScheduler()
    sched.add_job(foo, 'interval', seconds=5)
    sched.start()
    sleep(20)
    sched.shutdown()

    
    port = serial.Serial(port='/dev/ttyUSB0',
                         baudrate=9600,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE)
    smallLeft = bytearray.fromhex('1b401d10111b6100')
    nextLine  = bytearray.fromhex('0d0a')
    bigCenter = bytearray.fromhex('1b401d21111b6101')
    port.write(smallLeft)
    port.write(b'Your Free-Air Code Is:')
    port.write(nextLine)
    port.write(bigCenter)
    port.write(b'Code')
    port.write(nextLine)
    port.write(nextLine)
    port.write(nextLine)
    port.write(smallLeft)
    print("Written.")
    """
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
    
