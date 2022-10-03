from lib.FileOp import Config

def main():
    config = Config('/home/pi/CMS/')
    print(config.getSize())
    config.newSize(17000)
    print(config.getSize())

if __name__ == '__main__':
    main()
