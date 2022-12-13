import robot
import serial_tools
import acquisition
import tools
import platform

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

    pread = robot.Point(name='vect[1]')

    robot.get_point_coordinates(ser, pread)

    pread.print()
