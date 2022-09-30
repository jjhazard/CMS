#OS operations
import os
#Multithreading
from threading import Thread
from time import sleep
#Database
from lib.FileOp import Dispatched
from datetime import datetime, timedelta
#Update
from apscheduler.schedulers.background import BackgroundScheduler
#Devices
from lib.Devices import Transceiver, Relay, Keypad, Buzzer

####################################
#        PROGRAM VARIABLES         #
####################################
#Path variables
folderPath = '/home/pi/CMS/Codes/'
date = datetime.today()
dispatched = Dispatched(folderPath, date)
#Update variable
sched = BackgroundScheduler()
#Device variables
transceiver = Transceiver()
keypad = Keypad()
buzzer = Buzzer()
relay = Relay()
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
sched.add_job(update, 'cron', day='*', hour='0', minute='0')
sched.start()

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

    #Start Subprocesses
    keypad_handler = Thread(target=keypadMonitor)
    keypad_handler.start()
    communicator = Thread(target=commsMonitor)
    communicator.start()

    #Continuously check subprocesses are running
    try:
        while True:
            if not communicator.is_alive():
                communicator = Thread(target=commsMonitor)
                communicator.start()
            if not keypad_handler.is_alive():
                keypad_handler = Thread(target=keypadMonitor)
                keypad_handler.start()
            #sleep(60)
    #if anything goes wrong, stop the subprocesses and the scheduler
    except Exception as e:
        global running
        running = False
    global sched
    sched.shutdown()
    
#Allows program to be run from bash script
if __name__ == '__main__':
    CVS()
