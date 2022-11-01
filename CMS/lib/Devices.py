import board
import digitalio
from time import sleep
from datetime import datetime, timedelta

class Transceiver:
    def program(self, code_system):
        self.rfm69.encryption_key = (b"\x45\x78\x63\x65\x6C\x20\x54\x69\x72\x65\x20\x47\x61\x75\x67\x65")
        if code_system == 'CRS':
            self.rfm69.node = 1
            self.rfm69.destination = 2
        else:
            self.rfm69.node = 2
            self.rfm69.destination = 1
    def __init__(self, code_system):
        from adafruit_rfm69 import RFM69
        from threading import Lock
        from busio import SPI
        CS = digitalio.DigitalInOut(board.CE1)
        RESET = digitalio.DigitalInOut(board.D25)
        spi = SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm69 = RFM69(spi, CS, RESET, 915.0)
        self.program(code_system)
        self.lastCode = ''
        self.lock = Lock()
    def receive(self):
        with self.lock:
            packet = self.rfm69.receive(timeout=5)
        try:
            return str(packet, 'ascii')
        except:
            return None
    def __sendSignal(self, code):
        with self.lock:
            self.rfm69.send(bytearray(code, 'ascii'))
    def __sendVerify(self, code):
        with self.lock:
            sending = True
            while sending:
                self.rfm69.send(bytearray(code, 'ascii'))
                status = self.rfm69.receive(timeout=3.0)
                if status == b'valid':
                    sending = False
    def send(self, code):
        self.__sendVerify(code)
    def reset(self):
        self.__sendVerify("reset")
    def valid(self, code):
        self.lastCode = code
        self.__sendSignal("valid")
    def invalid(self):
        self.__sendSignal("invalid")

class Relay(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D1)
        self.switch_to_output()
        self.value = 0
    def activate(self):
        self.value = 1
        sleep(3)
        self.value = 0

class Button(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D24)
        self.switch_to_input(pull=digitalio.Pull.UP)
        self.__pressed = False
    def new(self):
        if self.value:
            self.__pressed = False
        elif self.__pressed:
            return False
        else:
            self.__pressed = True
        return self.__pressed

class Numberpad(digitalio.DigitalInOut):
    def __init__(self):
        import evdev
        from time import time
        super().__init__(board.D24)
        self.switch_to_output()
        self.value = 0
        self.time = time
        self.pressed = evdev.ecodes.EV_KEY
        self.decipher = evdev.categorize
        self.port = evdev.InputDevice('/dev/input/event0')
        self.port.grab()
        self.keys = {'KEY_0': '0', 'KEY_1': '1',
                     'KEY_2': '2', 'KEY_3': '3',
                     'KEY_4': '4', 'KEY_5': '5',
                     'KEY_6': '6', 'KEY_7': '7',
                     'KEY_8': '8', 'KEY_9': '9'}
        self.special = False
        self.code = ''
        self.start = 0
    def clear(self):
        self.code = ''
        self.start = 0
    def beep(self):
        self.value = 1
        sleep(0.1)
        self.value = 0
    def reject(self):
        self.clear()
        for buzz in range(3):
            self.beep()
            sleep(0.07)
    def getCode(self):
        while True:
            event = self.port.read_one()
            if not (event and event.type == self.pressed):
                if self.start and self.time()-self.start > 5:
                    self.reject()
                continue
            key = self.decipher(event)
            if not key.keystate:
                continue
            self.time = event.sec
            self.beep()
            if key.scancode == 42:
                self.special = True
            elif self.special:
                self.special = False
                if key.scancode == 4:
                    return self.code 
                else:
                    self.reject()
            else:
                self.code += self.keys[key.keycode]

class Printer:
    def __init__(self):
        import serial
        self.port = serial.Serial(port='/dev/ttyUSB0',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE)
        self.smallLeft = bytearray.fromhex('1b401d10111b6100')
        self.nextLine  = bytearray.fromhex('0d0a')
        self.bigCenter = bytearray.fromhex('1b401d21111b6101')
        self.feedLines = bytearray.fromhex('0a0a0a0a')
    def print(self, code):
        self.port.write(self.smallLeft)
        self.port.write(b'Your Free-Air Code Is:')
        self.port.write(self.nextLine)
        self.port.write(self.bigCenter)
        self.port.write(bytearray(code, 'ascii'))
        self.port.write(self.nextLine)
        self.port.write(self.smallLeft)
        self.port.write(b'Code is valid through tomorrow')
        self.port.write(self.nextLine)
        self.port.write(b'and expires upon use. Enjoy!')
        self.port.write(self.nextLine)
        self.port.write(self.feedLines)
