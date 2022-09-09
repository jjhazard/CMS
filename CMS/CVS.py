#OS operations
import os
#Multithreading
from threading import Thread, Lock
#Database
from FileOp import FileOpen, FolderMod, FileMod
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
import Update
#Pins
import board
import digitalio
#Keypad
import adafruit_matrixkeypad

####################################
#        PROGRAM VARIABLES         #
####################################
#Path variables
folderPath = '/home/pi/CMS/CVSCodes/'
dispatched = '{}{}'.format(folderPath, 'Dispatched/')
expired = '{}{}'.format(folderPath, 'Expired/')
date = datetime.today().strftime('%Y.%m.%d')
#Keypad variables
cols = [digitalio.DigitalInOut(x) for x in (board.D2, board.D3, board.D4)]
rows = [digitalio.DigitalInOut(x) for x in (board.D25, board.D23, board.D7, board.D8)]
keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
keys = keypad.pressed_keys
inputting = False
keypad_code = ''
#Update variable
sched = BackgroundScheduler()
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
"""
Temporary class while lora transciever not in program
"""
class Receive(FileMod):
    def execute(self):
        code = self.old_file.read(5)
        self.close()
        if code == '':
            os.remove(self.new_name)
        return code
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
sched.add_job(update, 'interval', day='*', hour='0', minute='0')
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
#if one key is pressed, add that key to the code
def getKeyIfOne(keys):
    global keypad_code
    if len(keys) == 1:
        keypad_code = '{}{}'.format(keypad_code, keys[0])

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
    global keys
    global keypad_code
    global inputting
    getKeyIfOne(keys)
    pressed = keys
    last_press = datetime.now()
    while len(keypad_code) < 5 and (datetime.now() - last_press).total_seconds() > 5:
        keys = keypad.pressed_keys
        if not pressed == keys:
            getKeyIfOne(keys)
            pressed = keys
            last_press = datetime.now()
    if validate(keypad_code):
        Add(expired, keypad_code).execute()
        #activate unit
    else:
        print("Failed to find") #Tell customer of failure
    keypad_code = ''
    inputting = False

####################################
#     COMMUNICATION OPERATIONS     #
####################################
def receive():
    code = Receive('/home/pi/CMS/CommPlaceholder/comms').execute() #Receive from Lora transciever
    if code: #Verify received a valid code
        Add(dispatched, code).execute()
    else:
        print("Bad Code: ", code)
def communicate():
    return os.path.exists('/home/pi/CMS/CommPlaceholder/comms') #Check for comms

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
            if not inputting:
                keys = keypad.pressed_keys
                if keys and not (pressed == keys):
                    test = test + 1
                    inputting = True
                    keypadInput()
                """
                if not (keypad_handler or keypad_handler.is_alive()) :
                    keypad_handler = Thread(target=keypadInput)
                    keypad_handler.start()
                    keypad_handler.join()
                """
            #If incoming signal, process it
            if communicate():
                test = test + 1
                receive()
                """
                if not (communicator or communicator.is_alive()) :
                    communicator = Thread(target=receive)
                    communicator.join()
                """
    except KeyboardInterrupt:
        pass
    global sched
    sched.shutdown()
if __name__ == '__main__':
    CVS()
#005230023300673003770095500145007760012300202002480026300083009200019200322001890015500268005200062700751
