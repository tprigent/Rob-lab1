import robot
import serial_tools
import acquisition


if __name__ == '__main__':

    # define input image
    image_name = 'test_draw_1.png'
    width, height = acquisition.get_image_format(image_name)

    # image processing
    print("\n### IMAGE PROCESSING ###")
    keypoints = acquisition.build_path(image_name, 100, gen_video=0)

    # serial connect
    ser = serial_tools.connect_serial('COM3')
    if ser is None: exit(-1)

    # origin definition
    print("\n### ORIGIN DEFINITION ###")
    p0 = robot.Point()  # reference point
    input("-> Please set robot to origin (and press enter)")

    # point frame conversion
    print("\n### POINT FRAME CONVERSION ###")
    vector = robot.get_key_point_vector(keypoints, p0, width, height, 1000)
    robot.get_point_coordinates(ser, p0)
    p0.print_point()
    user_check = input("-> Is origin correct (y|n)")
    if user_check.lower() != 'y': exit(-1)

    # record vector in robot memory
    print("\n### RECORDING POINTS IN ROBOT ###")
    vector_name = 'path'
    robot.record_vector(ser, vector, vector_name)

    # start drawing
    print("\n### START DRAWING ###")
    robot.draw_vector(ser, vector_name)
