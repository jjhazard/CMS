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

class Buzzer(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D24)
        self.switch_to_output()
        self.value = 0
    def reject(self):
        for buzz in range(3):
            self.value = 1
            sleep(0.1)
            self.value = 0
            sleep(0.07)
    def buzz(self):
        self.value = 1
        sleep(0.1)
        self.value = 0

class Button(digitalio.DigitalInOut):
    def __init__(self):
        super().__init__(board.D17)
        self.switch_to_input(pull=digitalio.Pull.DOWN)
    def held(self):
        end = datetime.now() + timedelta(milliseconds=800)
        while datetime.now() < end:
            if not self.value:
               return False
        return True

class Numberpad(adafruit_matrixkeypad.Matrix_Keypad):
    def __init__(self):
        self.keys = {'KEY_0': '0', 'KEY_1': '1',
                     'KEY_2': '2', 'KEY_3': '3',
                     'KEY_4': '4', 'KEY_5': '5',
                     'KEY_6': '6', 'KEY_7': '7',
                     'KEY_8': '8', 'KEY_9': '9'}
        self.special = False
        import evdev
        self.port = evdev.InputDevice('/dev/input/event0')
        self.port.grab()
        self.pressed = evdev.ecodes.EV_KEY
        self.decipher = evdev.categorize
        self.code = ''
        self.time = 0
        self.buzzer = Buzzer()
    def clear(self):
        self.code = ''
        self.time = 0
    def reject(self):
        self.clear()
        self.buzzer.reject()
    def now(self):
        return datetime.now().timestamp()
    def getCode(self):
        while True:
            event = self.port.read_one()
            if not event:
                if self.time and not self.now-self.time < 5:
                    self.reject()
                continue
            if event.type == self.pressed:
                self.time = event.sec
                key = self.decipher(event)
                if key.keystate:
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
