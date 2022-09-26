#OS operations
import os
#Multithreading
from threading import Thread, Lock
#Database
from lib.FileOp import Available, Dispatched, Expired, Queue
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
import lib.Update as Update
#Pins
import board
import digitalio
#Devices
from lib.Devices import Transceiver, Button
from lib.Serial import Printer
from time import sleep

####################################
#        PROGRAM VARIABLES         #
####################################
#File management variables
folderPath = '/home/pi/CMS/CRSCodes/'
size = 1000
date = datetime.today()
available  = Available(folderPath)
dispatched = Dispatched(folderPath, date)
expired    = Expired(folderPath, date)
queue      = Queue(folderPath)
file_system = Lock()
#Update scheduler
sched = BackgroundScheduler()
#Device variables
transceiver = Transceiver()
request = Button()
printer = Printer()

####################################
#         Startup Check            #
####################################
#verifyDatabase ensures program directories and available file exist before execution
def verifyDatabase():
    global available
    global dispatched
    global expired
    global size
    #Ensure each directories exists
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    dispatched.verify()
    expired.verify()

    #Ensure available file has codes, reset CVS if creating
    if not available.verify():
        available.create(1, size)
        global transceiver
        transceiver.reset()

####################################
#          UPDATE CODES            #
####################################
#Move or merge dispatched codes to the relevant expired files
#Merge outdated expired files with the available code set
def update():
    global file_system
    global dispatched
    global expired
    file_system.acquire()
    date = datetime.today()
    dispatched.date = date
    expired.date = date
    Update.Dispatched(dispatched.name, expired.name).execute()
    Update.Expired(available.name, expired.name).execute()
    file_system.release()
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
    global request
    global available
    global dispatched
    global queue
    code = available.get()
    printer.print(code) 
    dispatched.add(code)
    queue.add(code)
    sleep(1)
    request.release

#While the queue has codes
#Read the first code off the queue
#Communicate until confirmed received
#Remove the first item from the queue
def communicate():
    global tranceiver
    global queue
    while queue.exists():
        code = queue.read()
        if not code == '':
            transceiver.send(code)
            #transceiver.sent(code)
            queue.pop()
    transceiver.release

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
    try:
        while True:
            while not file_system.locked():
                if (not request.locked) and request.value:
                    request.acquire
                    request_handler = Thread(target=generate)
                    request_handler.start()

                #If the queue exists, empty it
                if (not transceiver.locked) and queue.exists():
                    transceiver.acquire
                    communicator = Thread(target=communicate)
                    communicator.start()
            sleep(1)
    except KeyboardInterrupt:
        pass
    global sched
    sched.shutdown()

if __name__ == '__main__':
    CRS()
