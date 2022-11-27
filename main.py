import time
import datetime
import serial_tools


if __name__ == '__main__':
    ser = serial_tools.connect_serial('COM3')

    if ser is not None:
        print('\n### BEGIN SEQUENCE ###')
        # Draw a flat square from given p0
        serial_tools.send(ser, 'DIMP square[4]')
        serial_tools.send(ser, 'HERE square[1]')
        serial_tools.send(ser, 'HERE square[2]')
        serial_tools.send(ser, 'SETPVC square[2] X 200')
        serial_tools.send(ser, 'HERE square[3]')
        serial_tools.send(ser, 'SETPVC square[2] Y 300')
        serial_tools.send(ser, 'HERE square[4]')
        serial_tools.send(ser, 'SETPVC square[4] X 200')
        serial_tools.send(ser, 'SETPVC square[4] Y 300')

        for i in range(4):
            msg1 = 'TEACH square[{}]'.format(i)
            serial_tools.send(ser, msg1)
            msg2 = 'MOVE square[{}]'.format(i)
            serial_tools.send(ser, msg2)
            msg3 = 'HERE square[{}]'.format(i)
            serial_tools.send(ser, msg3)

        serial_tools.send(ser, 'MOVES square 1 4')
