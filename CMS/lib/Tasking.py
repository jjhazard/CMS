from threading import Thread
import logging
#Callable class to check current state of program
#Allows reference to program state from anywhere
class State:
    def __init__(self):
        self.__on = False
    def __call__(self, *args, **kwargs):
        return self.__on
    #Only ever called from beginning of program
    def start(self):
        self.__on = True
    #Only ever called from exception block
    def stop(self):
        self.__on = False
#Thread that starts when created and restarts automatically
class RThread:
    def __init__(self, function, argList):
        self.function = function
        self.thread = Thread(target=function, args=argList)
        self.thread.start()
    def renew(self):
        if not self.thread.is_alive():
            self.thread = Thread(target=self.function)
            self.thread.start()
#Logger to write errors to file
class FLogger:
    def __init__(self):
        logging.basicConfig(filename='errorState.txt',
                           filemode='a',
                           format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                           datefmt='%D  %H:%M:%S',
                           level=logging.ERROR)
        self.logger = logging.getLogger('errorState')
    def error(self, message):
        self.logger.exception(message)