import time
import datetime
import tools


if __name__ == '__main__':
    ser = tools.connect_serial('COM3')

    if ser is not None:
        print('\n### BEGIN SEQUENCE ###')
        # Draw a flat square from given p0
        tools.send(ser, 'DIMP square[4]')
        tools.send(ser, 'HERE square[1]')
        tools.send(ser, 'HERE square[2]')
        tools.send(ser, 'SETPVC square[2] X 200')
        tools.send(ser, 'HERE square[3]')
        tools.send(ser, 'SETPVC square[2] Y 300')
        tools.send(ser, 'HERE square[4]')
        tools.send(ser, 'SETPVC square[4] X 200')
        tools.send(ser, 'SETPVC square[4] Y 300')

        for i in range(4):
            msg1 = 'TEACH square[{}]'.format(i)
            tools.send(ser, msg1)
            msg2 = 'MOVE square[{}]'.format(i)
            tools.send(ser, msg2)
            msg3 = 'HERE square[{}]'.format(i)
            tools.send(ser, msg3)

        tools.send(ser, 'MOVES square 1 4')
