import re
import serial_tools
import tools


class Point:
    def __init__(self, name='point', ptype='image', x=0, y=0, z=0, p=0, r=0):
        self.name = name
        self.ptype = ptype
        self.x = x
        self.y = y
        self.z = z
        self.p = p
        self.r = r

    def print(self):
        tools.print_title('\n### POINT {} coordinates (in {}) ###'.format(self.name, self.ptype))
        print('X={}  Y={}  Z={}  P={}  R={}'.format(self.x, self.y, self.z, self.p, self.r))


class Vector:
    def __init__(self, name='vector', points=None):
        self.name = name
        self.points = points

    def print(self):
        tools.print_title('\n### VECTOR {} ###'.format(self.name))
        for i in range(len(self.points)):
            pt = self.points[i]
            print('[{}] {} X={}  Y={}  Z={}  P={}  Z={}'.format(i, pt.name, pt.x, pt.y, pt.z, pt.p, pt.z))


# fills Point instance with robot memory data
def get_point_coordinates(ser=None, point=None):
    # get point info from robot
    serial_tools.send(ser, 'defp {}'.format(point.name))
    serial_tools.send(ser, 'here {}'.format(point.name))
    response = serial_tools.send(ser, 'listpv {}'.format(point.name))

    # run regex to extract coordinates
    regex = r"(?:X|Y|Z|P|R):.-?[0-9]*"
    coordinates = re.finditer(regex, response, re.MULTILINE)

    # fill Point structure
    i = 0
    for c in coordinates:
        coord = c.group().split(":", 1)[1]
        if i == 0:
            point.x = coord
        elif i == 1:
            point.y = coord
        elif i == 2:
            point.z = coord
        elif i == 3:
            point.p = coord
        elif i == 4:
            point.r = coord
        i += 1


# convert point related to image frame to the robot frame relatively to p0
# + add of r, p, and r coordinates info
def imgf_to_robf(point, p0, img_width, img_height, scale):
    unit_factor = max(img_width, img_height)
    point.x = int(p0.x) - int(point.x * (min(img_width, img_height) / unit_factor) * scale)
    point.y = int(p0.y) - int(point.y * (min(img_width, img_height) / unit_factor) * scale)     # Y axis reverted in robot frame
    point.z = p0.z
    point.p = p0.p
    point.r = p0.r
    point.ptype = 'robot'

    return respects_boundaries(point)


# function that converts key points to a vector
def get_vector_from_keypoints(keypoints, p0, name, img_width, img_height, scale):
    vect = Vector(name=name)
    vect.points = []
    reachability = 0
    for i in range(len(keypoints)):
        p = Point('p{}'.format(i), x=keypoints[i][0], y=keypoints[i][1])
        reachability |= imgf_to_robf(p, p0, img_width, img_height, scale)
        vect.points.append(p)
    return vect, reachability


# Check if a point respects the robot physical and environmental limits
def respects_boundaries(point):
    x_min = 3000
    x_max = 7000
    y_min = -800
    y_max = 2500
    return x_min < point.x < x_max and y_min < point.y < y_max


# Define a vector in the robot's memory
def record_vector(ser, vector):
    dim = len(vector.points)
    serial_tools.send(ser, 'DIMP {}[{}]'.format(vector.name, dim))
    c = 1
    for i in vector.points:
        if i.ptype == 'robot':

            # define point
            serial_tools.send(ser, 'HERE {}[{}]'.format(vector.name, c))

            if c > 1:   # if possible, copy point from previous one
                serial_tools.send(ser, 'SETP {}[{}]={}[{}]'.format(vector.name, c, vector.name, c-1))

            # send new x y coordinates each time
            serial_tools.send(ser, 'SETPVC {}[{}] X {}'.format(vector.name, c, vector.points[c-1].x))
            serial_tools.send(ser, 'SETPVC {}[{}] Y {}'.format(vector.name, c, vector.points[c-1].y))

            if c == 1:  # if first point, define coordinates
                serial_tools.send(ser, 'SETPVC {}[{}] Z {}'.format(vector.name, c, vector.points[c-1].z))
                serial_tools.send(ser, 'SETPVC {}[{}] P {}'.format(vector.name, c, vector.points[c-1].p))
                serial_tools.send(ser, 'SETPVC {}[{}] R {}'.format(vector.name, c, vector.points[c-1].r))

            c += 1  # increment vector counter

        else:
            print('Error: points still in the image frame')
            exit(-1)


# function that allows to move the robot along the vector of position "vector" from the position 1 to n
def draw_vector(ser, vector):
    n = len(vector.points)
    # move pen to first point
    serial_tools.send(ser, 'MOVE {}[1]'.format(vector.name), ask=1)
    # draw vector
    serial_tools.send(ser, 'MOVES {} 1 {}'.format(vector.name, n), ask=1)

