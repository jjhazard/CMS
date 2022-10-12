from time import sleep
import logging

def error():
    sleep(0.5)
    print("Slept, throwing 0")
    raise TypeError

def main():
    print("Running Test")
    logging.basicConfig(filename='state.txt',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                        datefmt='%D  %H:%M:%S',
                        level=logging.ERROR)
    logger = logging.getLogger('state')
    try:
        error()
    except:
        logger.exception('Error')
if __name__ == '__main__':
    main()
