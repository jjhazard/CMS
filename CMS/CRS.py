#Database
import os
from lib.FileOp import Available, Dispatched, Expired, Queue, Config
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
#Devices
from lib.Devices import Transceiver, Button, Printer
#Multithreading
from lib.Tasking import RThread
from time import sleep
####################################
#        PROGRAM VARIABLES         #
####################################
#File management variables
folderPath = '/home/pi/CMS/Codes/'
date       = datetime.today()
available  = Available(folderPath)
dispatched = Dispatched(folderPath, date)
expired    = Expired(folderPath, date)
queue      = Queue(folderPath)
config     = Config(folderPath)
if config.exists():
    size   = config.getSize()
else:
    size   = config.default()
#Update scheduler
sched = BackgroundScheduler()
#Device variables
transceiver = Transceiver()
printer = Printer()
request = Button()
#Subprocess Status
running = True

####################################
#           UPDATE DATA            #
####################################
#Move or merge dispatched codes to the relevant expired files
#Merge outdated expired files with the available code set
def update():
    global date
    global available
    global dispatched
    global expired
    global queue

    #Ensure directories and files exist
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    available.verify()
    dispatched.verify()
    expired.verify()

    #If the size of stored data doesn't match expected size, reset data
    total_size = available.size()
    total_size += dispatched.size()
    total_size += expired.size()
    if not (total_size / 5) == size:
        available.delete()
        dispatched.delete()
        expired.delete()
        queue.delete()
        available.createCodes(1, size)
        global transceiver
        transceiver.reset()

    #Update saved dates
    date = datetime.today()
    dispatched.date = date
    expired.date = date

    #Merge any 2 day old dispatched files to expired file of same name
    expire_date = date - timedelta(days=2)
    for file in dispatched.list():
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < expire_date:
            expired.add(dispatched.dump(file), file)

    #merge any 14 day old expired files to available codes
    expire_date = date - timedelta(days=14)
    for file in expired.list():
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < expire_date:
            available.add(expired.dump(file))

#Start the scheduler (occurs when program starts)
sched.add_job(update, 'cron', day='*', hour='0', minute='0')
sched.start()

####################################
#          SUBPROCESSES            #
####################################
#Continously check for code request
#Get a random available code
#Print the code
#Dispatch the code
#Add the code to the queue
def requestMonitor():
    global running
    global size
    global request
    global available
    global dispatched
    global queue
    global printer
    tally = 0
    while running:
        if request.value:
            code = available.get()
            printer.print(code)
            dispatched.add(code)
            queue.add(code)
            if available.size() < 100:
                new_size = size + 1000
                available.createCodes(size, new_size)
                size = new_size
                global config
                config.newSize(size)
            sleep(1)
            if tally == 5:
                printer.printError("Button constantly pressed.")
                running = False
            else:
                tally += 1
        else:
            tally = 0
#Continously check queue for codes
#Read the first code off the queue
#Communicate until confirmed received
#Remove the first item from the queue
def commsMonitor():
    global tranceiver
    global queue
    global running
    while running:
        if queue.exists():
            code = queue.read()
            transceiver.send(code)
            queue.pop()

####################################
#         MAIN DISPATCHER          #
####################################
#Code Request System
def CRS():
    global running
    try:
        #Ensure database exists and is up to date on startup
        update()

        #Start subprocesses
        request_handler = RThread(requestMonitor)
        communicator    = RThread(commsMonitor)

        #Continuously keep subprocesses running
        while running:
            request_handler.renew()
            communicator.renew()
            sleep(60)

    #if anything goes wrong, stop the subprocesses and the scheduler
    except Exception as e:
        running = False
    global sched
    sched.shutdown()
    os.system("shutdown /s /t 1")

#Allows program to be run from bash script
if __name__ == '__main__':
    CRS()
