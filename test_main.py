import platform

import robot
import serial_tools
import acquisition
import tools


if __name__ == '__main__':
    # define input image
    image_name = 'test_draw_1.png'
    width, height = acquisition.get_image_format(image_name)

    # image processing
    tools.print_title("### IMAGE PROCESSING ###")
    all_points = acquisition.get_ordered_points(image_name, gen_video=0)    # get ordered points
    class_points = acquisition.identify_class(all_points, image_name)    # separate points into class
    segments = acquisition.extract_segments_from_class(class_points)    # extract extrema for each class (segments)
    points = acquisition.extract_POI(segments)                          # downsample POI (eliminate nearest neighbours)
    #acquisition.draw_segments(points, image_name)                       # debug function: draw lines between points

    #test de la fonction
    acquisition.curve_path(points, all_points)