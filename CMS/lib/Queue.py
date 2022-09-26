import os
from threading import Lock
from lib.FileOp import FileOpen, FileMod
####################################
#          QUEUE CLASSES           #
####################################
#Class to add a code to the end of the queue
class Add(FileOpen):
    def __init__(self, path, code):
        self.code = code
        super().__init__(path, 'a')
    def execute(self):
        self.file.write(self.code)
        self.close()
#Class to read first code in queue
class Read(FileOpen):
    def __init__(self, path):
        super().__init__(path, 'r')
    def execute(self):
        code = self.file.read(5)
        self.close()
        return code
#Class to pop out the first code in the queue
class Pop(FileMod):
    def execute(self):
        self.old_file.read(5)
        self.close()
        if os.path.getsize(self.new_name) == 0:
            os.remove(self.new_name)

class Queue:

    def __init__(self, path):
        self.file = '{}{}'.format(path, 'queue')
        self.__lock = Lock()

    def add(self, code):
        self.__lock.acquire()
        queue = open(self.file, 'a')
        queue.write(code)
        queue.close()
        self.__lock.release()

    def read(self):
        self.__lock.acquire()
        queue = open(self.file, 'r')
        code = queue.read(5)
        queue.close()
        self.__lock.release()
        return code

    def pop(self):
        self.__lock.acquire()
        queue = FileMod(self.file)
        queue.old_file.read(5)
        queue.close()
        if os.path.getsize(self.file) == 0:
            os.remove(self.file)
        self.__lock.release()
