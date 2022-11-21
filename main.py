import time
import datetime
import tools


if __name__ == '__main__':
    ser = tools.connect_serial('COM3')

    if ser is not None:
        # let's go
        print("go")

