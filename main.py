import platform

import robot
import serial_tools
import acquisition
import tools


if __name__ == '__main__':

    # define serial port name
    if platform.system() == 'Darwin':
        serial_port = '/dev/ttys005'     # macOS
    else:
        serial_port = "COM3"                                # Windows

    # define input image
    image_name = 'test_draw_1.png'
    width, height = acquisition.get_image_format(image_name)

    # image processing
    tools.print_title("### IMAGE PROCESSING ###")
    keypoints = acquisition.build_path(image_name, 100, gen_video=0)

    # serial connect
    ser = serial_tools.connect_serial(serial_port)
    if ser is None: exit(-1)

    # origin definition
    tools.print_title("### ORIGIN DEFINITION ###")
    p0 = robot.Point(name='p0')  # reference point
    input("-> Please set robot to origin (and press enter) ")

    # point frame conversion
    tools.print_title("### POINT FRAME CONVERSION ###")
    robot.get_point_coordinates(ser, p0)
    v = robot.get_vector_from_keypoints(keypoints, p0, width, height, 1000)
    p0.print()
    user_check = input("-> Is origin correct (y|n) ")
    if user_check.lower() != 'y': exit(-1)

    # record vector in robot memory
    tools.print_title("### RECORDING POINTS IN ROBOT ###")
    robot.record_vector(ser, v)

    # start drawing
    tools.print_title("### START DRAWING ###")
    robot.draw_vector(ser, v)
