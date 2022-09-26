import board
import digitalio
import serial
import adafruit_matrixkeypad
from time import sleep
from datetime import datetime
from threading import Lock

class Transceiver():

    def __init__(self):
        self.__transmit = digitalio.DigitalInOut(board.D15)
        self.__transmit.switch_to_output()
        self.__receive = digitalio.DigitalInOut(board.D14)
        self.__receive.switch_to_input(pull=digitalio.Pull.DOWN)
        self.__delay = 0.009
        self.__signals = {"validation": '1111011101101000',
                               "reset": '1111111101010101',
                               "valid": '1111111100000000',
                             "invalid": '1111111111111111'}
        self.__lock = Lock()

    @property
    def locked(self):
        return self.__lock.locked()

    @property
    def acquire(self):
        self.__lock.acquire()

    @property
    def release(self):
        self.__lock.release()

    def receive(self):
        received = ''
        while len(received) < 300:
            received += str(int(self.__receive.value))
            sleep(self.__delay)
        segments = received.split(self.__signals["validation"])
        if len(segments) == 1:
            return None
        index = 0
        while index < len(segments):
            if len(segments[index]) == 16:
                index = index + 1
            else:
                segments.pop(index)
        return int(mode(segments), 2)

    def signal(self):
        return self.__receive.value

    def __sendSignal(self, code):
        for t in range(10):
            for bit in self.__signals["validation"]:
                self.__transmit.value = int(bit)
                sleep(self.__delay)
            for bit in code:
                self.__transmit.value = int(bit)
                sleep(self.__delay)

    def transmit(self, code): 
        code = '{0:016b}'.format(int(code))
        self.__sendSignal(code)

    def reset(self):
        self.__sendSignal(self.__signals["reset"])

    def valid(self):
        self.__sendSignal(self.__signals["valid"])
        
    def invalid(self):
        self.__sendSignal(self.__signals["invalid"])

class Printer:
    port = serial.Serial(port='/dev/ttyUSB0',
                         baudrate=9600,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE)
    smallLeft = bytearray.fromhex('1b401d10111b6100')
    nextLine  = bytearray.fromhex('0d0a')
    bigCenter = bytearray.fromhex('1b401d21111b6101')

    def print(self, code):
        self.port.write(self.smallLeft)
        self.port.write(b'Your Free-Air Code Is:')
        self.port.write(self.nextLine)
        self.port.write(self.bigCenter)
        self.port.write(bytearray(code, 'ascii'))
        self.port.write(self.nextLine)
        self.port.write(self.nextLine)
        self.port.write(self.smallLeft)

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
        super().__init__(board.D10)
        self.switch_to_input(pull=digitalio.Pull.DOWN)
        self.__lock = Lock()

    @property
    def locked(self):
        return self.__lock.locked()

    @property
    def acquire(self):
        self.__lock.acquire()

    @property
    def release(self):
        self.__lock.release()


class Keypad(adafruit_matrixkeypad.Matrix_Keypad):

    def __init__(self):
        cols = [digitalio.DigitalInOut(x) for x in (board.D12, board.D16, board.D20)]
        rows = [digitalio.DigitalInOut(x) for x in (board.D6, board.D13, board.D19, board.D26)]
        keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
        super().__init__(rows, cols, keys)
        self.saved_keys = []
        self.code = ''
        self.__lock = Lock()

    @property
    def locked(self):
        return self.__lock.locked()

    @property
    def acquire(self):
        self.__lock.acquire()

    @property
    def release(self):
        self.__lock.release()


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
