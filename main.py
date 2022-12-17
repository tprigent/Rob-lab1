import platform

import robot
import serial_tools
import acquisition
import tools


if __name__ == '__main__':

    # define serial port name
    if platform.system() == 'Darwin':
        serial_port = '/dev/ttys004'     # macOS
    else:
        serial_port = "COM3"             # Windows

    # serial connect
    ser = serial_tools.connect_serial(serial_port)
    if ser is None: exit(-1)

    # home
    tools.print_title("### HOME ROBOT ###")
    #home = input("-> Do you want to set robot to home position ? (y|n) ")
    #if home.lower() == 'y': serial_tools.send(ser, 'home')

    # define input image
    image_name = 'test_draw_1.png'
    width, height = acquisition.get_image_format(image_name)

    # image processing
    tools.print_title("### IMAGE PROCESSING ###")
    all_points = acquisition.get_ordered_points(image_name, gen_video=0)    # get ordered points
    class_points = acquisition.identify_class(all_points, image_name)    # separate points into class
    segments = acquisition.extract_segments_from_class(class_points)    # extract extrema for each class (segments)
    points = acquisition.extract_POI(segments)                          # downsample POI (eliminate nearest neighbours)
    acquisition.draw_segments(points, image_name)                       # debug function: draw lines between points

    # origin definition
    tools.print_title("### ORIGIN DEFINITION ###")
    #p0 = robot.Point(name='p0')  # reference point
    p0 = robot.Point(name='p0', x=4960, y=1841, z=1716, p=-840, r=-202, ptype='robot')
    #input("-> Please set robot to origin (and press enter) ")

    # point frame conversion
    tools.print_title("### POINT FRAME CONVERSION ###")
    robot.get_point_coordinates(ser, p0)
    v, reachability = robot.get_vector_from_keypoints(points, p0, 'vect', width, height, scale=1000,rotate90=1)
    if reachability == 0:       # check reachability of all points
        print("-> Some points are not reachable. Please select another p0, orientation or reconsider the scale value.")
    p0.print()                  # reference check
    user_check = input("-> Is origin correct ? (y|n) ")
    if user_check.lower() != 'y': exit(-1)

    # record vector in robot memory
    tools.print_title("### RECORDING POINTS IN ROBOT ###")
    robot.record_vector(ser, v)

    # start drawing
    tools.print_title("### START DRAWING ###")
    robot.draw_vector(ser, v)
    robot.draw_circ_vector(ser,v)