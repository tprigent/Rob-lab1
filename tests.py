import acquisition
import robot
import serial_tools
import platform
import cv2

if __name__ == '__main__':

    # define serial port name
    if platform.system() == 'Darwin':
        serial_port = '/dev/cu.usbserial-14110'     # macOS
    else:
        serial_port = "COM3"

    ser = serial_tools.connect_serial(serial_port)

    p0 = robot.Point('first', x=5300, y=300, z=1010, p=-822, r=-175)
    p1 = robot.Point('sec', x=5000, y=300, z=1010, p=-822, r=-175)
    p2 = robot.Point('th', x=5000, y=500, z=1010, p=-822, r=-175)
    p3 = robot.Point('four', x=5300, y=500, z=1010, p=-822, r=-175)

    v = robot.Vector('vect')
    v.points = []
    v.points.append(p0)
    v.points.append(p1)
    v.points.append(p2)
    v.points.append(p3)


    # robot.record_vector(ser, v)
    # robot.draw_vector(ser, v)

    image_name = 'test_draw_1.png'

    points = acquisition.get_ordered_keypoints(image_name, 21, gen_video=1)

    img = cv2.imread('input-images/{}'.format(image_name))
    for i in range(len(points)-2):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        cv2.line(img, (y1, x1), (y2, x2), (0, 255, 0), 10)

    cv2.imwrite('output-images/robot-result.png'.format(image_name), img)
