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
            file = open(file_name, 'a')
            file.write('{0:05d}'.format(num)) 
            file.close()
            file_name = '{}{}'.format(self.expired, self.date.strftime("%Y.%m.%d"))
            file = open(file_name, 'a')
            file.write('{0:05d}'.format(num)) 
            file.close()
            self.date = self.date - timedelta(days = 1)
