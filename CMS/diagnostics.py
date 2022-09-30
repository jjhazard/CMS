from lib import Devices, FileOp
import os
from datetime import datetime, timedelta

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
    inputting = True
    while inputting:
        status = input("Received TEST print? (Y/N) ")
        status = status.upper()
        if status == 'Y':
            print("Printer: SUCCESS")
            inputting = False
        elif status == 'N':
            print("Printer: FAILURE")
            inputting = False
        else:
            print("Invalid input, type y or n.")

def CRS():
    assertButton()
    assertPrinter()

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
