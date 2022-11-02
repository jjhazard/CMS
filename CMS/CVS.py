#Database
import os
from lib.FileOp import Dispatched
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
#Devices
from lib.Devices import Transceiver, Relay, Numberpad
#Threads
from lib.Tasking import State, RThread, FLogger
from time import sleep
#Errors
import logging
####################################
#        PROGRAM VARIABLES         #
####################################
#Path variables
folderPath = '/home/excel/CMS-main/CMS/Codes/'
date = datetime.today()
dispatched = Dispatched(folderPath, date)
#Update variable
sched = BackgroundScheduler()
#Program State
running = State()
#Device variables
transceiver = Transceiver(running, 'CVS')
numberpad = Numberpad(running)
relay = Relay()
#Logger variable
logger = FLogger()
####################################
#             Update               #
####################################
#update deletes any outdated files
def update():
    global date
    global dispatched
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    dispatched.verify()
    date = datetime.today()
    dispatched.date = date
    expire_date = date - timedelta(days=2)
    for file in dispatched.list():
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < expire_date:
            dispatched.remove(file)

####################################
#          SUBPROCESSES            #
####################################
#Continuously check the numberpad for input
#If input found, process it
#If valid, expire code and activate unit
#If invalid, activate the buzzer
def numberpadMonitor():
    global numberpad
    global relay
    global running
    while running():
        code = numberpad.getCode()
        if len(code) == 4 and dispatched.find(code):
            numberpad.clear()
            relay.activate()
        else:
            numberpad.reject()

#Continously check transceiver for signal
#If reset signal, erase all saved codes
#If code is invalid, send invalid signal
#If code is valid, save and send valid signal
def commsMonitor():
    global transceiver
    global dispatched
    global running
    while running():
        code = transceiver.receive()
        if not code:
            continue
        if transceiver.lastCode != code:
            if code == "reset":
                transceiver.valid(code)
                dispatched.delete()
            elif not (code.isnumeric() and len(code) == 4):
                transceiver.invalid()
            else:
                transceiver.valid(code)
                dispatched.add(code)
        else:
            transceiver.valid(code)

####################################
#            DISPATCHER            #
####################################
def CVS():
    #Start the CVS
    global running
    running.start()

    #Ensure database exists and is up to date on startup
    update()

    #Start subprocesses
    numberpad_handler = RThread(attempt, [numberpadMonitor, "Failure to validate code."])
    communicator   = RThread(attempt, [commsMonitor, "Failure to communicate codes."])

    #Continuously keep subprocesses running
    while running():
        numberpad_handler.renew()
        communicator.renew()
        sleep(60)

#if anything goes wrong, stop running and log the error
def attempt(function, errorMessage):
    global running
    global logger
    try:
        function()
    except:
        running.stop()
        logger.error(errorMessage)
    
#Start the scheduler (occurs when program starts)
sched.add_job(attempt,
              args=[update, 'Failed to update'],
              trigger='cron',
              day='*',
              hour='0',
              minute='0')

#Allows program to be run from bash script
if __name__ == '__main__':
    sched.start()
    attempt(CVS, ["Failure in dispatcher."])
    sched.shutdown()
    exit(1)
