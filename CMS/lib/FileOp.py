import os
from random import randrange
from threading import Lock
####################################
#   FILE OPERATION BASE CLASSES    #
####################################
#Base file class for reading or appending to files
class FileOpen:
    def prep(self, path, mode):
        self.name = path
        self.file = open(path, mode)
    def __init__(self, path, mode):
        self.prep(path, mode)
    def execute(self):
        pass
    def close(self):
        self.file.close()
#Base file class for modifying a file and changing its length
class FileMod:
    def prep(self, name):
        self.size = os.path.getsize(name)
        self.new_name = name
        self.old_name = '{}{}'.format(name, '2')
        os.rename(self.new_name, self.old_name)
        self.new_file = open(self.new_name, 'w')
        self.old_file = open(self.old_name, 'r')
    def __init__(self, name):
        self.prep(name)
    def execute(self):
        pass
    def close(self):
        self.new_file.write(self.old_file.read())
        self.new_file.close()
        self.old_file.close()
        os.remove(self.old_name)
#Base folder class for reading or appending a file with data from a folder
class FolderOpen(FileOpen):
    def operate(self, file):
        pass
    def execute(self):
        files = os.listdir(self.folder)
        for file in files:
            self.operate(file)
#Base folder class for modifying a file with data from a folder
class FolderMod(FileMod):

    def __init__(self, folder, code):
        self.folder = folder
        self.code = code
        self.found = False

    def operate(self, file):
        end = False
        self.prep('{}{}'.format(self.folder, file))
        while not end:
            test_code = self.old_file.read(5)
            if test_code == self.code:
                self.found = True
                self.close()
                return
            elif test_code == '':
                end = True
            else:
                self.new_file.write(test_code)
        self.close()

    def execute(self):
        files = os.listdir(self.folder)
        for file in files:
            self.operate(file)

class FileLock:

    def verify(self):
        if not os.path.exists(self.name):
            os.mkdir(self.name)

class Queue(FileLock):

    def __init__(self, path):
        self.name = '{}{}'.format(path, 'queue')
        self.__lock = Lock()

    def exists(self):
        return os.path.exists(self.name)

    def add(self, code):
        self.__lock.acquire()
        file = open(self.name, 'a')
        file.write(code)
        file.close()
        self.__lock.release()

    def read(self):
        self.__lock.acquire()
        queue = open(self.name, 'r')
        code = queue.read(5)
        queue.close()
        self.__lock.release()
        return code

    def pop(self):
        self.__lock.acquire()
        queue = FileMod(self.name)
        queue.old_file.read(5)
        queue.close()
        if os.path.getsize(self.name) == 0:
            os.remove(self.name)
        self.__lock.release()

class Dispatched(FileLock):

    def __init__(self, path, date):
        self.name = '{}{}'.format(path, 'Dispatched/')
        self.__lock = Lock()
        self.date = date

    def add(self, code):
        self.__lock.acquire()
        file = open('{}{}'.format(self.name, self.date.strftime('%Y.%m.%d')), 'a')
        file.write(code)
        file.close()
        self.__lock.release()

    def find(self, code):
        self.__lock.aquire()
        dispatched = FolderMod(self.name, code)
        dispatched.execute()
        self.__lock.release()        
        return dispatched.found

class Expired(FileLock):

    def __init__(self, path, date):
        self.name = '{}{}'.format(path, 'Expired/')
        self.__lock = Lock()
        self.date = date

    def add(self, code):
        self.__lock.acquire()
        file = open('{}{}'.format(self.name, self.date.strftime('%Y.%m.%d')), 'a')
        file.write(code)
        file.close()
        self.__lock.release()

class Available(FileLock):

    def __init__(self, path):
        self.name = '{}{}'.format(path, 'available')
        self.__lock = Lock()

    def verify(self):
        if not os.path.exists(self.name):
            return False
        return True

    def get(self):
        self.__lock.acquire()
        file = FileMod(self.name)
        index = randrange(0, file.size, step=5)
        file.new_file.write(file.old_file.read(index))
        code = file.old_file.read(5)
        file.close()
        self.__lock.release()
        return code

    def create(self, start, stop):
        self.__lock.acquire()
        file = open(self.name, 'a')
        for code in range(start, stop):
            file.write('{0:05d}'.format(code))
        file.close()
        self.__lock.release()
