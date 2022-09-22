#OS operations
import os
#Multithreading
from threading import Thread, Lock
#Database
from lib.FileOp import FileOpen, FolderMod, FileMod
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
dispatched = '{}{}'.format(folderPath, 'Dispatched/')
expired = '{}{}'.format(folderPath, 'Expired/')
date = datetime.today().strftime('%Y.%m.%d')
#Update variable
sched = BackgroundScheduler()
#Keypad variables
keypad = Keypad()
keypad_lock = Lock()
#Comms variable
transceiver = Transceiver()
transceiver_lock = Lock()
#Relay variable
relay = Relay()
#Buzzer variable
buzzer = Buzzer()
####################################
#           CVS CLASSES            #
####################################
#Class to add a code to the dispatched code file
class Add(FileOpen):
    def __init__(self, path, code):
        self.code = code
        super().__init__(path + datetime.now().strftime("%Y.%m.%d"), 'a')
    def execute(self):
        self.file.write(self.code)
        self.close()
#Validate a code and expire it
class Validate(FolderMod):
    def __init__(self, folder, code):
        self.folder = folder
        self.code = code
        self.found = False
    def operate(self, file):
        end = False
        self.prep('{}{}'.format(self.folder, file))
        while not end:
            test_code = self.old_file.read(5)
            if test_code == self.code:
                self.found = True
                self.close()
                return
            elif test_code == '':
                end = True
            else:
                self.new_file.write(test_code)
        self.close()
        return False

####################################
#             Update               #
####################################
def update():
    global date
    date = datetime.today().strftime('%Y.%m.%d')
    print("Updated CVS at ", datetime.now())
    Update.Dispatched(dispatched, expired).execute()
    files = os.listdir(expired)
    expire_date = datetime.now() - timedelta(days=14)
    for file in files:
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < expire_date:
            os.remove('{}{}'.format(expired, file))
sched.add_job(update, 'cron', day='*', hour='0', minute='0')
sched.start()

####################################
#         Startup Check            #
####################################
#verify_folders ensures program directories exist before execution
#creates them if not present
def verifyFolders():
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    if not os.path.exists(dispatched):
        os.mkdir(dispatched)
    if not os.path.exists(expired):
        os.mkdir(expired)

####################################
#        KEYPAD OPERATIONS         #
####################################
#Check the dispatched directory for the given code
def validate(code):
    valid = Validate(dispatched, code)
    valid.execute()
    return valid.found

#Check the keypad until the code is 5 digits long
#If a button press takes 5 seconds, quit
#Validate the input
#If valid, expire code and activate unit
def keypadInput():
    global keypad
    global relay
    global buzzer
    keypad.processInput()
    if not keypad.code == '-----' and validate(keypad.code):
        Add(expired, keypad.code).execute()
        print("Activate")
        relay.activate()
    else:
        print("Failure: " + keypad.code)
        buzzer.activate()
    keypad.code = ''
    keypad_lock.release()

####################################
#     COMMUNICATION OPERATIONS     #
####################################
def receive():
    global transceiver
    global transceiver_lock
    code = transceiver.receive()
    if code and code < 16000:
        Add(dispatched, '{0:05d}'.format(code)).execute()
        transceiver.valid()
    else:
        transceiver.invalid()
    transceiver_lock.release()

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

    #Actual code is:
    """
    while True:
        keys = keypad.pressed_keys
        if keys and not (pressed == keys):
            test = test + 1
            getKeyIfOne(keys)
            keypadInput()
    """
    #Test code is:
    test = 0
    try:
        while test < 5:
            if not keypad_lock.locked():
                keypad.saveKeys()
                if keypad.saved_keys and not (pressed == keypad.saved_keys):
                    test = test + 1
                    keypad_lock.acquire()
                    keypadInput()
                    """
                    keypad_handler = Thread(target=keypadInput)
                    keypad_handler.start()
                    keypad_handler.join()
                    """
            #If incoming signal, process it
            if not transceiver_lock.locked():
                if transceiver.signal():
                    test = test + 1
                    receive()
                    """
                    communicator = Thread(target=receive)
                    communicator.join()
                    """
    except KeyboardInterrupt:
        pass
    global sched
    sched.shutdown()

if __name__ == '__main__':
    CVS()
