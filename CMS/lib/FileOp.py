import os
from random import randrange
from threading import Lock

#Context manager that allows shortening of a file
class FileMod:
    def __init__(self, name):
        self.size = os.path.getsize(name)
        self.write_name = name
        self.read_name = '{}{}'.format(name, '2')
        os.rename(self.write_name, self.read_name)
    def __enter__(self):
        self.write_file = open(self.write_name, 'w')
        self.read_file = open(self.read_name, 'r')
        return self
    def write(self, packet):
        self.write_file.write(packet)
    def read(self, byte_num=None):
        if byte_num:
            return self.read_file.read(byte_num)
        return self.read_file.read()
    def seek(self, byte_num):
        self.write_file.write(self.read_file.read(byte_num))
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.write_file.write(self.read_file.read())
        self.write_file.close()
        self.read_file.close()
        os.remove(self.read_name)
#File lock to guard a file from multi-access
class FileLock:
    def __init__(self, path, file_name):
        self.name = '{}{}'.format(path, file_name)
        self.lock = Lock()    
    def delete(self):
        with self.lock:
            if os.path.exists(self.name):
                os.remove(self.name)
    def exists(self):
        with self.lock:
            return os.path.exists(self.name)
    def verify(self):
        with self.lock:
            if not os.path.exists(self.name):
                file = open(self.name, 'w')
                file.close()
    def size(self):
        with self.lock:
            return os.path.getsize(self.name)
    def getFilePath(self, file=None):
        return self.name
    def add(self, packet, file=None):
        with self.lock, open(self.getFilePath(file), 'a') as file:
            file.write(packet)
#Folder lock to guard a folder from multi-access
class FolderLock(FileLock):
    def __init__(self, path, name, date):
        super().__init__(path, name)
        self.date = date
    def delete(self):
        with self.lock:
            if os.path.exists(self.name):
                for file_name in os.listdir(self.name):
                    os.remove(self.getFilePath(file_name))
    def verify(self):
        with self.lock:
            if not os.path.exists(self.name):
                os.mkdir(self.name)
    def size(self):
        with self.lock:
            size = 0
            for file_name in os.listdir(self.name):
                size += os.path.getsize(self.getFilePath(file_name))
            return size
    def list(self):
        with self.lock:
            return os.listdir(self.name)
    def getFilePath(self, file_name=None):
        if file_name:
            return '{}{}'.format(self.name, file_name)
        return '{}{}'.format(self.name, self.date.strftime('%Y.%m.%d'))
    def dump(self, file_name):
        with self.lock, open(self.getFilePath(file_name), 'r') as file:
            packet = file.read()
        os.remove(self.getFilePath(file_name))
        return packet
    def remove(self, file_name):
        with self.lock:
            os.remove(self.getFilePath(file_name))
#Protected available file
class Available(FileLock):
    def __init__(self, path):
        super().__init__(path, "available")
    def get(self):
        with self.lock, FileMod(self.name) as file:
            index = randrange(0, file.size, step=5)
            file.seek(index)
            return file.read(5)
    def createCodes(self, start, stop):
        with self.lock, open(self.name, 'a') as file:
            for code in range(start, stop):
                file.write('{0:05d}'.format(code))
#Protected queue file
class Queue(FileLock):
    def __init__(self, path):
        super().__init__(path, "queue")
    def read(self):
        with self.lock, open(self.name, 'r') as file:
            return file.read(5)
    def pop(self):
        if self.size() <= 5:
            self.delete()
        else:
            with self.lock, FileMod(self.name) as queue:
                queue.read(5)
#Protected config file
class Config(FileLock):
    def __init__(self, path):
        super().__init__(path, "config.txt")
    def default(self):
        self.newSize(10000)
        return 10000
    def getSize(self):
        with self.lock, open(self.name, 'r') as file:
            return int(file.read()[5:])
    def newSize(self, size):
        with self.lock, open(self.name, 'w') as file:
            file.write('{}{}'.format("size=", str(size)))
#Protected Dispatched folder
class Dispatched(FolderLock):
    def __init__(self, path, date):
        super().__init__(path, 'Dispatched/', date)
    def find(self, code):
        files = self.list()
        for file_name in files:
            with self.lock, FileMod(self.getFilePath(file_name)) as file:
                searching = True
                while searching:
                    test_code = file.read(5)
                    if test_code == code:
                        return True
                    elif test_code == '':
                        searching = False
                    else:
                        file.write(test_code)
        return False
#Protected Expired Folder
class Expired(FolderLock):
    def __init__(self, path, date):
        super().__init__(path, 'Expired/', date)
