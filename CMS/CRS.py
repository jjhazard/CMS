#OS operations
import os
#Multithreading
from threading import Thread, Lock
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
#Devices
from lib.Devices import Transceiver, Printer, Button
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
#Update variable
sched = BackgroundScheduler()
#Request variables
request = Button()
request_lock = Lock()
printer = Printer()
#Comms variable
transceiver = Transceiver()
transceiver_lock = Lock()

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

    #Ensure available file has codes, reset CVS if creating
    if not os.path.exists(available):
        if os.path.getsize(available) == 0:
            for file in os.scandir(dispatched):
                os.remove(file)
            for file in os.scandir(expired):
                os.remove(file)
        availableFile = open(available, 'a')
        for code in range(1, 1001):
            availableFile.write('{0:05d}'.format(code))
        availableFile.close()
        global transceiver
        transceiver.reset()

####################################
#          UPDATE CODES            #
####################################
#Move or merge dispatched codes to the relevant expired files
#Merge outdated expired files with the available code set
def update():
    global date
    date = datetime.today().strftime('%Y.%m.%d')
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
    global request_lock
    code = Get(available).execute()
    printer.print(code) 
    Add(dispatched, code).execute()
    Queue.Add(queue, code).execute()
    sleep(1)
    request_lock.release()

#While the queue has codes
#Read the first code off the queue
#Communicate until confirmed received
#Remove the first item from the queue
def communicate():
    global tranceiver
    global comms_lock
    if os.path.getsize(queue) == 0:
        os.remove(queue)
    while os.path.exists(queue):
        code = Queue.Read(queue).execute()
        if not code == '':
            transceiver.transmit(code)
            Queue.Pop(queue).execute()
    transceiver_lock.release()

####################################
#         MAIN DISPATCHER          #
####################################
#Code Request System
def CRS():

    #Ensure database exists and is up to date on startup
    verifyDatabase()
    update()

    #Create subprocess variables
    request_handler = None
    communicator = None

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
            if not request_lock.locked() and request.value:
                test = test + 1
                request_lock.acquire()
                generate()
                """
                request_handler = Thread(target=generate)
                request_handler.start()
                """
            #If the queue exists, empty it
            if not transceiver_lock.locked() and os.path.exists(queue):
                transceiver_lock.acquire()
                communicate()
                """
                communicator = Thread(target=communicate)
                communicator.start()
                """
    except KeyboardInterrupt:
        pass
    global sched
    sched.shutdown()

if __name__ == '__main__':
    CRS()
