#OS operations
import os
#Multithreading
from threading import Thread, Lock
#Database
from lib.FileOp import Dispatched
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
import lib.Update as Update
#Pins
import board
import digitalio
#Keypad
import adafruit_matrixkeypad
#Tranceive
from lib.Devices import Transceiver, Relay, Keypad, Buzzer

####################################
#        PROGRAM VARIABLES         #
####################################
#Path variables
folderPath = '/home/pi/CMS/CVSCodes/'
date = datetime.today()
dispatched = Dispatched(folderPath, date)
#Update variable
sched = BackgroundScheduler()
#Keypad variables
keypad = Keypad()
#Comms variable
transceiver = Transceiver()
packet = None
#Relay variable
relay = Relay()
#Buzzer variable
buzzer = Buzzer()
####################################
#             Update               #
####################################
def update():
    global date
    global dispatched
    date = datetime.today()
    print("Updated CVS at ", datetime.now())
    expire_date = date - timedelta(days=2)
    for file in dispatched.list():
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < expire_date:
            dispatched.remove(file)
sched.add_job(update, 'cron', day='*', hour='0', minute='0')
sched.start()

####################################
#         Startup Check            #
####################################
#verify_folders ensures program directories exist before execution
#creates them if not present
def verifyFolders():
    global dispatched
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    dispatched.verify()

####################################
#        KEYPAD OPERATIONS         #
####################################
#Check the keypad until the code is 5 digits long
#If a button press takes 5 seconds, quit
#Validate the input
#If valid, expire code and activate unit
def keypadInput():
    global keypad
    global relay
    global buzzer
    while True:
        keypad.processInput()
        if not keypad.code == '-----' and dispatched.find(keypad.code):
            print("Activate")
            relay.activate()
        else:
            print("Failure: " + keypad.code)
            buzzer.activate()
        keypad.code = ''

####################################
#     COMMUNICATION OPERATIONS     #
####################################
def receive():
    global transceiver
    global dispatched
    last_code = None
    while True:
        code = transceiver.receive()
        if code:
            if code == "reset":
                dispatched.delete()
            elif code != last_code:
                dispatched.add('{0:05d}'.format(code))
                last_code = code
                transceiver.valid()

####################################
#            DISPATCHER            #
####################################
def CVS():

    #Ensure database exists and is up to date on startup
    verifyFolders()
    update()

    #Create subprocess variables
    keypad_handler = None
    communicator = None

    #Loop continuously
    global keys
    global inputting
    global tranceiver
    pressed = []

    try:
        while True:
            if not keypad.locked:
                keypad.saveKeys()
                if keypad.saved_keys and not (pressed == keypad.saved_keys):
                    keypad.acquire
                    keypad_handler = Thread(target=keypadInput)
                    keypad_handler.start()
                #If incoming signal, process it
            if (not transceiver.locked) and transceiver.signal():
                transceiver.acquire
                communicator = Thread(target=receive)
                communicator.start()
     except KeyboardInterrupt:
        pass
    global sched
    sched.shutdown()

if __name__ == '__main__':
    CVS()
