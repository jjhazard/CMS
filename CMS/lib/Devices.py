import board
import busio
import serial
import digitalio
import adafruit_matrixkeypad
import adafruit_rfm69
from time import sleep
from datetime import datetime, timedelta
from threading import Lock
from statistics import mode

class Transceiver:
    def __init__(self):
        CS = digitalio.DigitalInOut(board.CE1)
        RESET = digitalio.DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
        self.lock = Lock()
    def receive(self):
        self.lock.acquire()
        packet = self.rfm69.receive(timeout=5)
        if packet:
            return str(packet, 'ascii')
        return None
        self.lock.release()
    def __sendSignal(self, code, verify):
        self.lock.acquire()
        sending = True
        while sending:
            self.rfm69.send(bytearray(code))
            if verify:
                status = self.rfm69.receive(timeout=3.0)
                if status == b'valid':
                    sending == False
            else:
                sending = False
        self.lock.release()
    def send(self, code):
        self.__sendSignal(code, True)
    def reset(self):
        self.__sendSignal("reset", True)
    def valid(self):
        self.__sendSignal("valid", False)
    def invalid(self):
        self.__sendSignal("invalid", False)

class Relay(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D1)
        self.switch_to_output()
        self.value = 0
    def activate(self):
        self.value = 1
        sleep(5)
        self.value = 0

class Buzzer(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D0)
        self.switch_to_output()
        self.value = 0
    def activate(self):
        for buzz in range(3):
            self.value = 1
            sleep(0.1)
            self.value = 0
            sleep(0.07)

class Button(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D17)
        self.switch_to_input(pull=digitalio.Pull.DOWN)

class Keypad(adafruit_matrixkeypad.Matrix_Keypad):
    def __init__(self):
        cols = [digitalio.DigitalInOut(x) for x in (board.D12, board.D16, board.D20)]
        rows = [digitalio.DigitalInOut(x) for x in (board.D6, board.D13, board.D19, board.D26)]
        keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
        super().__init__(rows, cols, keys)
        self.saved_keys = []
        self.code = ''
    def saveKeys(self):
        self.saved_keys = self.pressed_keys
    def getKeyIfOne(self):
        if len(self.saved_keys) == 1:
            self.code = '{}{}'.format(self.code, self.saved_keys[0])
            sleep(0.2)
    def processInput(self):
        self.getKeyIfOne()
        pressed = []
        last_press = datetime.now()
        while len(self.code) < 5:
            if (datetime.now() - last_press).total_seconds() > 5:
                self.code = '-----'
            else:
                self.saveKeys()
                if not pressed == self.saved_keys:
                    self.getKeyIfOne()
                    pressed = self.saved_keys
                    last_press = datetime.now()
            sleep(0.1)

class Printer:
    def __init__(self):
        self.port = serial.Serial(port='/dev/ttyUSB0',
                         baudrate=9600,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE)
        self.smallLeft = bytearray.fromhex('1b401d10111b6100')
        self.nextLine  = bytearray.fromhex('0d0a')
        self.bigCenter = bytearray.fromhex('1b401d21111b6101')
    def print(self, code):
        self.port.write(self.smallLeft)
        self.port.write(b'Your Free-Air Code Is:')
        self.port.write(self.nextLine)
        self.port.write(self.bigCenter)
        self.port.write(bytearray(code, 'ascii'))
        self.port.write(self.nextLine)
        self.port.write(self.nextLine)
        self.port.write(self.smallLeft)
