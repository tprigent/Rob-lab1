import platform
import time
import robot
import serial_tools
import acquisition
import tools


if __name__ == '__main__':

    # STEP 1 : define serial port name
    if platform.system() == 'Darwin':
        serial_port = '/dev/ttys004'     # macOS
    else:
        serial_port = "COM3"             # Windows

    # serial connect
    ser = serial_tools.connect_serial(serial_port)
    if ser is None: exit(-1)

    # STEP 2 (optional): home
    tools.print_title("### HOME ROBOT ###")
    home = input("-> Do you want to set robot to home position ? (y|n) ")
    if home.lower() == 'y': serial_tools.send(ser, 'home')

    # STEP 3: image processing
    tools.print_title("### IMAGE PROCESSING ###")
    image_name = 'test_draw_2.png'
    width, height = acquisition.get_image_format(image_name)

    all_points = acquisition.get_ordered_points(image_name, gen_video=0)    # get ordered points
    class_points = acquisition.identify_class(all_points, image_name)   # separate points into class
    segments = acquisition.extract_segments_from_class(class_points)    # extract extrema for each class (segments)
    line_points = acquisition.extract_POI(segments)                     # downsample POI (eliminate nearest neighbours)
    acquisition.draw_segments(line_points, image_name, 'lines.png')       # debug function: draw lines between points
    curve_points = acquisition.curve_approx(all_points, line_points, 200)    # add points to the curved path to improve shape
    curve_points = acquisition.curve_approx(all_points, curve_points, 500)    # add points to the curved path to improve shape
    print(len(curve_points))
    acquisition.draw_segments(curve_points, image_name, 'curve.png')       # debug function: draw lines between points

    # STEP 4: origin definition
    tools.print_title("### ORIGIN DEFINITION ###")
    #p0 = robot.Point(name='p0')  # reference point
    p0 = robot.Point(name='p0', x=6200, y=1841, z=1716, p=-840, r=-202, ptype='robot')
    #input("-> Please set robot to origin (and press enter) ")

    # STEP 5: point frame conversion (image to robot)
    tools.print_title("### POINT FRAME CONVERSION ###")
    robot.get_point_coordinates(ser, p0)
    v, reachability = robot.get_vector_from_keypoints(curve_points, p0, 'vect', width, height, scale=0.4, rotate90=0)
    if reachability == 0:       # check reachability of all points
        print("-> Some points are not reachable. Please select another p0, orientation or reconsider the scale value.")
    p0.print()                  # reference check
    robot.draw_in_robot_environment(p0, v)
    user_check = input("-> Is origin correct ? (y|n) ")
    if user_check.lower() != 'y': exit(-1)

    # STEP 6: record vector in robot memory
    chrono = time.perf_counter()
    tools.print_title("### RECORDING POINTS IN ROBOT ###")
    robot.record_vector(ser, v)

    # STEP 7: start drawing
    tools.print_title("### START DRAWING ###")
    robot.draw_vector(ser, v)
    robot.draw_circ_vector(ser, v)

    # END : result
    elapsed_time = time.perf_counter() - chrono
    tools.print_title(f'Elapsed time: {elapsed_time:.2f} seconds')