"""
from threading import Thread
from CRS import CRS
from CVS import CVS
"""
import board
import digitalio
import time
from threading import Thread, Lock
from statistics import mode
from lib.Test import Create
import os
import stat
from time import sleep
from lib.Queue import Queue
extended_delay = 0.009
queue = Queue("/home/pi/CMS/CRSCodes/queue")
transmit = digitalio.DigitalInOut(board.D4)
transmit.switch_to_output()
def transmission(code):
    global short_delay
    global extended_delay
    global transmit
    global queue
    print("TR acquiring queue\n")
    queue.acquire
    print("TR got queue\n")
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
    print("TR released queue\n")
    queue.release

receive = digitalio.DigitalInOut(board.D14)
receive.switch_to_input(pull=digitalio.Pull.DOWN)
def reception():
    global short_delay
    global extended_delay
    global receive
    global queue
    print("RE acquiring queue\n")
    queue.acquire
    print("RE got queue\n")
    code = ''
    validation = '1111011101101000'
    while len(code) < 255:
        code += str(int(receive.value))
        time.sleep(extended_delay)
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
    print("RE released queue\n")
    queue.release

def main():
    path = '/home/pi/CMS/CRSCodes/Dispatched/'
    st = os.stat(path)
    print(st)
    if os.path.exists(path):
        print("cannot find")
#        os.mkdir(path)
    """
    for i in range(5):
        Create('/home/pi/CMS/CRSCodes/available',
               '/home/pi/CMS/CRSCodes/Dispatched/',
               '/home/pi/CMS/CRSCodes/Expired/').execute()
        Create('/home/pi/CMS/CVSCodes/available',
               '/home/pi/CMS/CVSCodes/Dispatched/',
               '/home/pi/CMS/CVSCodes/Expired/').execute()
    """
    t1 = Thread(target=transmission, args=[19206])
    t2 = Thread(target=reception)

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
    
if __name__ == '__main__':
    main()
    
