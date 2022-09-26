import os
from datetime import datetime, timedelta
from lib.FileOp import FolderOpen, FolderMod
####################################
#       UPDATE CODES CLASSES       #
####################################
#Class to update the Expired file directory
class Expired(FolderOpen):
    def __init__(self, available, expired):
        self.folder = expired
        self.date = datetime.now() - timedelta(days=14)
        super().__init__(available, 'a')
    def operate(self, file):
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < self.date:
            renewed_name = '{}{}'.format(self.folder, file)
            renewed_file = open(renewed_name, 'r')
            self.file.write(renewed_file.read())
            renewed_file.close()
            os.remove(renewed_name)
#Class to update the Expired file directory
class Dispatched(FolderMod):
    new_name = ''
    old_name = ''
    def prep(self):
        self.new_file = open(self.new_name, 'a')
        self.old_file = open(self.old_name, 'r')
    def __init__(self, dispatched, expired):
        self.folder = dispatched
        self.expired = expired
        self.date = datetime.now() - timedelta(days=2)
    def operate(self, file):
        file_date = datetime.strptime(file, '%Y.%m.%d')
        if file_date < self.date:
            self.old_name = '{}{}'.format(self.folder, file)
            self.new_name = '{}{}'.format(self.expired, file)
            if os.path.exists(self.new_name):
                self.prep()
                self.close()
            else:
                os.rename(self.old_name, self.new_name)
