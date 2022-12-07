import time
import datetime

import robot
import serial_tools
import acquisition


if __name__ == '__main__':
    image_name = 'test_draw_1.png'
    width, height = acquisition.get_image_format(image_name)
    p0 = robot.Point(x=200, y=5800, z=518, p=97845, r=120, ptype='robot')

    # image processing
    keypoints = acquisition.build_path(image_name, 100, gen_video=0)

    #acquisition.split(keypoints, image_name)

    # point processing
    vector = robot.get_key_point_vector(keypoints, p0, width, height, 1000)
    print('ok')


    ser = serial_tools.connect_serial('COM6')
    
    if ser is not None:
        robot.record_vector(ser, vector, 'test')

    ser = serial_tools.connect_serial('COM6')
    if ser is not None:
        vector_name = 'vector'
        robot.record_vector(ser, vector, vector_name)
        robot.draw_vector(ser, vector_name)
