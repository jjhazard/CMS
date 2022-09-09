#OS operations
import os
#Multithreading
from threading import Thread
#Database
from lib.FileOp import FileOpen, FileMod
from datetime import datetime, timedelta
from random import randrange
import lib.Queue as Queue
#Update
from apscheduler.schedulers.background import BackgroundScheduler
import lib.Update as Update
#Pins
import board
import digitalio
#Printer
from lib.Printer import Printer
from time import sleep

####################################
#        PROGRAM VARIABLES         #
####################################
#Paths
folderPath = '/home/pi/CMS/CRSCodes/'
dispatched = '{}{}'.format(folderPath, 'Dispatched/')
expired = '{}{}'.format(folderPath, 'Expired/')
available = '{}{}'.format(folderPath, 'available')
queue = '{}{}'.format(folderPath, 'queue')
date = datetime.today().strftime('%Y.%m.%d')
#Request Button
request = digitalio.DigitalInOut(board.D12)
request.switch_to_input(pull=digitalio.Pull.DOWN)
#Update variable
sched = BackgroundScheduler()
#Printer variable
printer = Printer()

####################################
#           CRS CLASSES            #
####################################
#Class to add a code to the dispatched code file
class Add(FileOpen):
    def __init__(self, path, code):
        self.code = code
        super().__init__(path + date, 'a')
    def execute(self):
        self.file.write(self.code)
        self.close()
#Class to pull a code from the available code file
class Get(FileMod):
    def execute(self):
        index = randrange(0, self.size, step=5)
        self.new_file.write(self.old_file.read(index))
        code = self.old_file.read(5)
        self.close()
        return code
"""
Temporary class while lora transciever not in program
"""
class Communicate(FileOpen):
    def __init__(self, code):
        self.code = code
        super().__init__('/home/pi/CMS/CommPlaceholder/comms', 'a')
    def execute(self):
        self.file.write(self.code)
        self.close()

####################################
#         Startup Check            #
####################################
#verifyDatabase ensures program directories and available file exist before execution
def verifyDatabase():

    #Ensure each directories exists
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    if not os.path.exists(dispatched):
        os.mkdir(dispatched)
    if not os.path.exists(expired):
        os.mkdir(expired)

    #if the available file doesn't exist, create it and write all viable codes
    try:
        availableFile = open(available, 'x') 
    except FileExistsError:
        pass
    else:
        for byte in range(1, 1001):
            string = str(byte)
            for char in range(5 - len(string)):
                string = '0' + string
            availableFile.write(string)
        availableFile.close()

####################################
#          UPDATE CODES            #
####################################
#Move or merge dispatched codes to the relevant expired files
#Merge outdated expired files with the available code set
def update():
    global date
    date = datetime.today().strftime('%Y.%m.%d')
    print("Updated CRS at ", datetime.now())
    Update.Dispatched(dispatched, expired).execute()
    Update.Expired(available, expired).execute()
sched.add_job(update, 'cron', day='*', hour='0', minute='0')
sched.start()

####################################
#          SUBPROCESSES            #
####################################
#Get a random available code
#Print the code
#Dispatch the code
#Add the code to the queue
def generate():
    global printer
    code = Get(available).execute()
    printer.print(code)
    Add(dispatched, code).execute()
    Queue.Add(queue, code).execute()
    sleep(1)

#While the queue has codes
#Read the first code off the queue
#Communicate until confirmed received
#Remove the first item from the queue
def communicate():
    while os.path.exists(queue):
        code = Queue.Read(queue).execute()
        Communicate(code).execute() #replace with transceiver call
        Queue.Pop(queue).execute()

####################################
#         MAIN DISPATCHER          #
####################################
#Code Request System
def CRS():

    #Ensure database exists and is up to date on startup
    verifyDatabase()
    update()

    #Create subprocess variables
    request_handler = Thread(target=generate)
    communicator = Thread(target=communicate)

    #Create a button tracker variable
    pressed = request.value

    #Loop continuously
    #Actual code is:
    """
    while True:
        if request.value and not pressed == request.value:
            pressed = request.value
    """
    #Test code is:
    test = 0
    try:
        while test < 5:
            if request.value and not pressed == request.value:
                test = test + 1

                pressed = request.value
                generate()
                """
                if not request_handler.is_alive():
                    request_handler.start()
                    request_handler.join()
                    request_handler = Thread(target=generate)
                """
            #If the queue exists, empty it
            if os.path.exists(queue):
                communicate()
                """
                if not communicator.is_alive():
                    communicator.start()
                    communicator.join()
                    communicator = Thread(target=communicate)
                """
    except KeyboardInterrupt:
        pass
    global sched
    sched.shutdown()

if __name__ == '__main__':
    CRS()
