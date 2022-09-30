from lib import Devices, FileOp
import os
from datetime import datetime, timedelta

def getUserInput(text, success=['Y'], failure=['N']):
    while True:
        status = input(text)
        status = status.upper()
        for condition in success:
            if status == condition:
                return condition
        for condition in failure:
            if status == condition:
                return None
        else:
            print("Invalid input.")
def getResult(text, name, success=['Y'], failure=['N']):
    if getUserInput(text, success=success, failure=failure):
        print(name + ": SUCCESS")
    else:
        print(name + ": FAILURE")
def assertButton():
    button = Devices.Button()
    start = datetime.now()
    end = start + timedelta(seconds=5)
    print("Press request button. (Timeout 5 seconds)")
    inputting = True
    while inputting and start < end:
        if button.value:
            inputting = False
        else:
            start = datetime.now()
    if start < end:
        print("Request: SUCCESS")
    else:
        print("Request: FAILURE")
def assertPrinter():
    printer = Devices.Printer()
    printer.print("TEST")
    getResult("Did TEST code print? (Y/N)", "Printer")
def assertRelay():
    relay = Devices.Relay()
    relay.activate()
    getResult("Relay Activated? (Y/N) ", "Relay")
def assertBuzzer():
    buzzer = Devices.Buzzer()
    buzzer.activate()
    getResult("Buzzer sound activated? (Y/N) ", "Buzzer")
def assertKeypad():
    keypad = Devices.Keypad()
    print("Type '01234' on the keypad.")
    success = [False, False, False]
    inputting = True
    attempts = 0
    while inputting and attempts < 3:
        keypad.saveKeys()
        if keypad.saved_keys:
            keypad.processInput()
            if keypad.code == '01234':
                inputting = False
                success[0] = True
            else:
                print("Try Again.")
                attempts += 1
            keypad.code = ''
    print("Type '56789' on the keypad.")
    inputting = True
    attempts = 0
    while inputting and attempts < 3:
        keypad.saveKeys()
        if keypad.saved_keys:
            keypad.processInput()
            if keypad.code == '56789':
                inputting = False
                success[1] = True
            else:
                print("Try Again.")
                attempts += 1
            keypad.code = ''
    print("Press any keypad button, then wait 5 seconds.")
    inputting = True
    attempts = 0
    while inputting and attempts < 3:
        keypad.saveKeys()
        if keypad.saved_keys:
            keypad.processInput()
            if keypad.code == '-----':
                inputting = False
                success[2] = True
            else:
                print("Try Again.")
                attempts += 1
            keypad.code = ''        
    print("Keypad 01234: ", "SUCCESS" if success[0] else "FAIL")
    print("Keypad 56789: ", "SUCCESS" if success[1] else "FAIL")
    print("Keypad Timeout: ", "SUCCESS" if success[2] else "FAIL")
def run(tests):
    index = 0
    while index < len(tests):
        input("Press any key to begin test. ")
        tests[index]()
        if not getUserInput("Repeat Test? (Y/N) "):
            index += 1
        else:
            print("Running test again...")
def CVS():
    tests = [assertRelay,
             assertBuzzer,
             assertKeypad]
    #TODO
    #-Transciever
    #-Data
    run(tests)
def CRS():
    tests = [assertButton,
             assertPrinter]
    #TODO
    #-Transciever
    #-Data
    run(tests)

def main():
    inputting = True
    while inputting:
        mode = input("Diagnosing CRS or CVS? ")
        mode = mode.upper()
        if mode == 'CRS' or mode == 'CVS':
            inputting = False
        else:
            print("Invalid input, type CRS or CVS.")
    if mode == 'CRS':
        CRS()
    else:
        CVS()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
