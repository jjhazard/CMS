import os
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
