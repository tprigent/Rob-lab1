import platform

import robot
import serial_tools
import acquisition


if __name__ == '__main__':

    # define serial port name
    if platform.system() == 'Darwin':
        serial_port = '/dev/cu.Bluetooth-Incoming-Port'     # macOS
    else:
        serial_port = "COM3"                                # Windows

    # define input image
    image_name = 'test_draw_1.png'
    width, height = acquisition.get_image_format(image_name)

    # image processing
    print("\n### IMAGE PROCESSING ###")
    keypoints = acquisition.build_path(image_name, 100, gen_video=0)

    # serial connect
    ser = serial_tools.connect_serial(serial_port)
    #if ser is None: exit(-1)

    # origin definition
    print("\n### ORIGIN DEFINITION ###")
    p0 = robot.Point(name='p0')  # reference point
    input("-> Please set robot to origin (and press enter)")

    # point frame conversion
    print("\n### POINT FRAME CONVERSION ###")
    robot.get_point_coordinates(ser, p0)
    v = robot.get_vector_from_keypoints(keypoints, p0, width, height, 1000)
    p0.print()
    user_check = input("-> Is origin correct (y|n)")
    if user_check.lower() != 'y': exit(-1)

    # record vector in robot memory
    print("\n### RECORDING POINTS IN ROBOT ###")
    robot.record_vector(ser, v)

    # start drawing
    print("\n### START DRAWING ###")
    robot.draw_vector(ser, v)
