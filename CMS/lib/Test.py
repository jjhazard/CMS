from datetime import datetime, timedelta
####################################
#     TEST GENERATION CLASSES      #
####################################
class Create():
    def __init__(self, available, dispatched, expired):
        self.available = available
        self.dispatched = dispatched
        self.expired = expired
        self.date = datetime.now()
    def execute(self):
        num = 0
        while num < 16:
            num = num + 1
            file_name = '{}{}'.format(self.dispatched, self.date.strftime("%Y.%m.%d"))
            try:
                file = open(file_name, 'x')
            except(FileExistsError):
                file = open(file_name, 'a')
            string = str(num)
            if len(string) == 1:
                file.write("0000" + string) 
            else:
                file.write("000" + string)
            file.close()
            file_name = '{}{}'.format(self.expired, self.date.strftime("%Y.%m.%d"))
            try:
                file = open(file_name, 'x')
            except(FileExistsError):
                file = open(file_name, 'a')
            string = str(num)
            if len(string) == 1:
                file.write("0000" + string) 
            else:
                file.write("000" + string)
            file.close()
            self.date = self.date - timedelta(days = 1)
