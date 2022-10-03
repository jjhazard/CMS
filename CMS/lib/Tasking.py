from threading import Thread

class RThread:
    def __init__(self, function):
        self.function = function
        self.thread = Thread(target=function)
        self.thread.start()
    def renew(self):
        if not self.thread.is_alive():
            self.thread = Thread(target=self.function)
            self.thread.start()
