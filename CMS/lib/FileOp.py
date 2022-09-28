import os
from random import randrange
from threading import Lock

class FileMod:
    def __init__(self, name):
        self.size = os.path.getsize(name)
        self.new_name = name
        self.old_name = '{}{}'.format(name, '2')
        os.rename(self.new_name, self.old_name)
        self.new_file = open(self.new_name, 'w')
        self.old_file = open(self.old_name, 'r')
    def write(self, packet):
        self.new_file.write(packet)
    def read(self, byte_num=None):
        if byte_num:
            return self.old_file.read(byte_num)
        return self.old_file.read()
    def seek(self, byte_num):
        self.new_file.write(self.old_file.read(byte_num))
    def close(self):
        self.new_file.write(self.old_file.read())
        self.new_file.close()
        self.old_file.close()
        os.remove(self.old_name)

class FileLock:
    def __init__(self, name):
        self.name = '{}{}'.format(path, name)
        self.lock = Lock()
    def delete(self):
        self.lock.acquire()
        os.remove(self.name)
        os.mkdir(self.name)
        self.lock.release()
    def exists(self):
        self.lock.acquire()
        return os.path.exists(self.name)
        self.lock.release()
    def verify(self):
        self.lock.acquire()
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        self.lock.release()
    def getFilePath(self, file=None):
        return self.name
    def add(self, packet, file=None):
        self.lock.acquire()
        file = open(self.getFileName(file), 'a')
        file.write(packet)
        file.close()
        self.lock.release()

class FolderLock(FileLock):
    def __init__(self, path, name, date):
        super().__init__(path, name)
        self.date = date
    def list(self):
        self.lock.acquire()
        files = os.listdir(self.name)
        self.lock.release()
        return files
    def getFilePath(self, file=None):
        if file:
            return '{}{}'.format(self.name, file)
        return '{}{}'.format(self.name, self.date.strftime('%Y.%m.%d'))
    def dump(self, name):
        self.lock.acquire()
        file = open(self.getFilePath(name), 'r')
        packet = file.read()
        file.close()
        os.remove(self.getFilePath(name))
        self.lock.release()
        return packet
    def remove(self, file):
        self.lock.acquire()
        os.remove(self.getFilePath(name))
        self.lock.release()
        
class Available(FileLock):
    def __init__(self, path):
        super().__init__(path, "available")
    def get(self):
        self.lock.acquire()
        file = FileMod(self.name)
        index = randrange(0, file.size, step=5)
        file.seek(index)
        code = file.read(5)
        file.close()
        self.lock.release()
        return code
    def create(self, start, stop):
        self.lock.acquire()
        file = open(self.name, 'a')
        for code in range(start, stop):
            file.write('{0:05d}'.format(code))
        file.close()
        self.lock.release()

class Queue(FileLock):
    def __init__(self, path):
        super().__init__(path, "queue")
    def read(self):
        self.lock.acquire()
        queue = open(self.name, 'r')
        code = queue.read(5)
        queue.close()
        self.lock.release()
        return code
    def pop(self):
        self.lock.acquire()
        queue = FileMod(self.name)
        queue.read(5)
        queue.close()
        if os.path.getsize(self.name) == 0:
            os.remove(self.name)
        self.lock.release()

class Dispatched(FolderLock):
    def __init__(self, path, date):
        super().__init__(path, 'Dispatched/', date)
    def find(self, code):
        self.lock.acquire()
        files = os.listdir(self.name)
        for file_name in files:
            file = FileMod(self.getFilePath(file_name))
            searching = True
            while searching:
                test_code = file.read(5)
                if test_code == code:
                    file.close()
                    self.lock.release()
                    return True
                elif test_code == '':
                    searching = False
                else:
                    file.write(test_code)
            file.close()
        self.lock.release() 
        return False

class Expired(FolderLock):
    def __init__(self, path, date):
        super().__init__(path, 'Expired/', date)
