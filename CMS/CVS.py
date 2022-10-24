#Database
import os
from lib.FileOp import Dispatched
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
#Devices
from lib.Devices import Transceiver, Relay, Keypad, Buzzer
#Threads
from lib.Tasking import RThread, FLogger
from time import sleep
#Errors
import logging
####################################
#        PROGRAM VARIABLES         #
####################################
#Path variables
folderPath =
date = datetime.today()
dispatched = Dispatched(folderPath, date)
#Update variable
sched = BackgroundScheduler()
#Device variables
transceiver = Transceiver()
keypad = Keypad()
buzzer = Buzzer()
relay = Relay()
#Logger variable
logger = FLogger()
#Subprocess Status
running = True
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
    print("Updated CVS at ", datetime.now())
    expire_date = date - timedelta(days=2)
    for file in dispatched.list():
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < expire_date:
            dispatched.remove(file)

####################################
#          SUBPROCESSES            #
####################################
#Continuously check the keypad for input
#If input found, process it
#If valid, expire code and activate unit
#If invalid, activate the buzzer
def keypadMonitor():
    global keypad
    global relay
    global buzzer
    global running
    while running:
        keypad.saveKeys()
        if keypad.saved_keys:
            keypad.processInput()
            if not keypad.code == '-----' and dispatched.find(keypad.code):
                relay.activate()
            else:
                buzzer.activate()
            keypad.code = ''

#Continously check transceiver for signal
#If reset signal, erase all saved codes
#If code is invalid, send invalid signal
#If code is valid, save and send valid signal
def commsMonitor():
    global transceiver
    global dispatched
    global running
    while running:
        code = transceiver.receive()
        if code:
            if transceiver.lastCode != code:
                if code == "reset":
                    transceiver.valid(code)
                    dispatched.delete()
                elif not (code.isnumeric() and len(code) < 6):
                    transciever.invalid()
                else:
                    transceiver.valid(code)
                    dispatched.add(code.zfill(0))
            else:
                transceiver.valid(code)

####################################
#            DISPATCHER            #
####################################
def CVS():
    #Ensure database exists and is up to date on startup
    update()

    #Start subprocesses
    keypad_handler = RThread(attempt, [keypadMonitor, "Failure to validate code."])
    communicator   = RThread(attempt, [commsMonitor, "Failure to communicate codes."])

    #Continuously keep subprocesses running
    global running
    while running:
        keypad_handler.renew()
        communicator.renew()
        sleep(60)

#if anything goes wrong, stop running and log the error
def attempt(function, errorMessage):
    try:
        function()
    except Exception as e:
        global running
        global logger
        running = False
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
