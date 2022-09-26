import serial
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
