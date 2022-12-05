import time
import datetime

import robot
import serial_tools
import acquisition


if __name__ == '__main__':
    image_name = 'test_draw_1.png'
    acquisition.build_path(image_name, 200, 1)

# ser = serial_tools.connect_serial('COM3')
    #
    # if ser is not None:
    #     print('\n### BEGIN SEQUENCE ###')
    #     # Draw a flat square from given p0
    #     serial_tools.send(ser, 'SPEED 20')
    #     serial_tools.send(ser, 'DIMP square[4]')
    #     serial_tools.send(ser, 'HERE square[1]')
    #     serial_tools.send(ser, 'HERE square[2]')
    #     serial_tools.send(ser, 'SETPVC square[2] X 200')
    #     serial_tools.send(ser, 'HERE square[3]')
    #     serial_tools.send(ser, 'SETPVC square[2] Y 300')
    #     serial_tools.send(ser, 'HERE square[4]')
    #     serial_tools.send(ser, 'SETPVC square[4] X 200')
    #     serial_tools.send(ser, 'SETPVC square[4] Y 300')
    #
    #     for i in range(4):
    #         msg1 = 'TEACH square[{}]'.format(i)
    #         serial_tools.send(ser, msg1)
    #         msg2 = 'MOVE square[{}]'.format(i)
    #         serial_tools.send(ser, msg2)
    #         msg3 = 'HERE square[{}]'.format(i)
    #         serial_tools.send(ser, msg3)
    #
    #     serial_tools.send(ser, 'MOVES square 1 4')
    #
    #     #Creation of a table_points in order to try the function
    #     #Z will be found thanks to P0 by hand
    #     pos_1 = robot.Point(name='pos_1', ptype='robot', x=0, y=0, z=0, p=0, r=0)
    #     pos_2 = robot.Point(name='pos_2', ptype='robot', x=200, y=0, z=0, p=0, r=0)
    #     pos_3 = robot.Point(name='pos_1', ptype='robot', x=200, y=200, z=0, p=0, r=0)
    #     pos_4 = robot.Point(name='pos_4', ptype='robot', x=0, y=200, z=0, p=0, r=0)
    #     table_points = [pos_1, pos_2, pos_3, pos_4]
    #     vector_name = 'vector'
    #     robot.record_vector(ser, table_points, vector_name)
    #     robot.draw_vector(ser, vector_name)
    #
