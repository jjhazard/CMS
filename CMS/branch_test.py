"""
from threading import Thread
from CRS import CRS
from CVS import CVS
"""
import board
import digitalio
import time
import threading
from statistics import mode
from lib.Test import Create
import os

extended_delay = 0.009

transmit = digitalio.DigitalInOut(board.D4)
transmit.switch_to_output()
def transmission(code):
    global short_delay
    global extended_delay
    global transmit
    code = '{0:016b}'.format(int(code))
    print(code)
    validation = '1111011101101000'
    for t in range(10):
        for bit in validation:
            transmit.value = int(bit)
            time.sleep(extended_delay)
        for bit in code:
            transmit.value = int(bit)
            time.sleep(extended_delay)

receive = digitalio.DigitalInOut(board.D14)
receive.switch_to_input(pull=digitalio.Pull.DOWN)
def reception():
    global short_delay
    global extended_delay
    global receive
    code = ''
    validation = '1111011101101000'
    while len(code) < 255:
        code += str(int(receive.value))
        time.sleep(extended_delay)
    print(code)
    segments = code.split(validation)
    if len(segments) == 1:
        print("Failed receive.")
    else: 
        index = 0
        while index < len(segments):
            if len(segments[index]) == 16:
                index = index + 1
            else:
                segments.pop(index)
    print(mode(segments))
    print(int(mode(segments), 2))
def main():
    """
    file = open('/home/pi/CMS/CVSCodes/Dispatched/2022.09.192', 'w')
    file.close()
    os.remove('/home/pi/CMS/CVSCodes/Dispatched/2022.09.192')

    file = open('/home/pi/CMS/CVSCodes/Dispatched/2022.09.192', 'w')
    file.close()
    os.remove('/home/pi/CMS/CVSCodes/Dispatched/2022.09.192')
    """
    for i in range(5):
        Create('/home/pi/CMS/CRSCodes/available',
               '/home/pi/CMS/CRSCodes/Dispatched/',
               '/home/pi/CMS/CRSCodes/Expired/').execute()
        Create('/home/pi/CMS/CVSCodes/available',
               '/home/pi/CMS/CVSCodes/Dispatched/',
               '/home/pi/CMS/CVSCodes/Expired/').execute()
    """
    try:
        while True:
            t1 = threading.Thread(target=transmission, args=[19206])
            t2 = threading.Thread(target=reception)

            # starting thread 1
            t1.start()
            # starting thread 2
            t2.start()

            # wait until thread 1 is completely executed
            t1.join()
            # wait until thread 2 is completely executed
            t2.join()
         
            # both threads completely executed
            print("Done!")
    except KeyboardInterrupt:
        pass
    """
if __name__ == '__main__':
    main()
    
