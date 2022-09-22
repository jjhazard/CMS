import os
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
    def operate(self, file):
        pass
    def execute(self):
        files = os.listdir(self.folder)
        for file in files:
            self.operate(file)
