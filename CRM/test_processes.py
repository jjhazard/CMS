from Verify import verifyDatabase
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
import Update
import CRS
import CVS
import Test
import Queue
import os
import time
import digitalio
import board
import adafruit_matrixkeypad

folderPath = '/home/pi/CRM/Codes/'
available = '{}{}'.format(folderPath, 'available')
dispatched = '{}{}'.format(folderPath, 'Dispatched/')
expired = '{}{}'.format(folderPath, 'Expired/')
queue = '{}{}'.format(folderPath, 'queue')
cols = [digitalio.DigitalInOut(x) for x in (board.D2, board.D3, board.D4)]
rows = [digitalio.DigitalInOut(x) for x in (board.D25, board.D23, board.D7, board.D8)]
keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
request = digitalio.DigitalInOut(board.D12)
request.switch_to_input(pull=digitalio.Pull.DOWN)
keypad_code = ''

def validate(code):
    valid = CVS.Validate(dispatched, code)
    valid.execute()
    return valid.found

def getNext(last_keys):
    global keypad_code
    #Get pressed key
    keys = keypad.pressed_keys

    #If the last key is the same as the current key, wait
    if keys == last_keys:
        return False, last_keys

    #If not exactly 1 key pressed, wait
    if not len(keys) == 1:
        return True, keys

    #Add the current key to the code
    keypad_code = '{}{}'.format(keypad_code, keys[0])
    return True, keys

def readKeypad():
    global keypad_code
    try:
        while True:
            if request.value:
                print("Getting Code")
                keys = None
                last_press = datetime.now()
                while len(keypad_code) < 5:
                    change, keys = getNext(keys)
                    if change:
                        last_press = datetime.now()
                    elif (datetime.now() - last_press).total_seconds() > 5:
                        keypad_code = ''
                        print("5s passed, abort")
                        break
                print(keypad_code)
    except KeyboardInterrupt:
        GPIO.cleanup()

def main():

    verifyDatabase()
    mode = input('Which mode?\nfileCreate = 0, testUpdate = 1, testFunctions = 2\n')
    if mode == "0":
        Test.Create(available, dispatched, expired).execute()
    elif mode == "1":
        Update.Dispatched(dispatched, expired).execute()
        Update.Expired(available, expired).execute()
    elif mode == "2":
        code = CRS.Get(available).execute()
        CRS.Add(dispatched, code).execute()
        code = input("What is your code? ")
        if validate(code):
            CVS.Add(expired, code).execute()
        else:
            print("Failed to find code.")

if __name__ == '__main__':
    main()

#Process Test
"""
    # creating thread
    t1 = threading.Thread(target=print_square, args=(10,))
    t2 = threading.Thread(target=print_cube, args=(10,))
 
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
"""

#InputTest
"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RECEIVE_PIN, GPIO.IN)
    cumulative_time = 0
    beginning_time = datetime.now()
    print '**Started recording**'
    while cumulative_time < MAX_DURATION:
        time_delta = datetime.now() - beginning_time
        RECEIVED_SIGNAL[0].append(time_delta)
        RECEIVED_SIGNAL[1].append(GPIO.input(RECEIVE_PIN))
        cumulative_time = time_delta.seconds
    print '**Ended recording**'
    print len(RECEIVED_SIGNAL[0]), 'samples recorded'
    GPIO.cleanup()
"""
