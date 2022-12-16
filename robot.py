import re
import serial_tools
import tools


class Point:
    def __init__(self, name='point', ptype='robot', x=0, y=0, z=0, p=0, r=0):
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


# create a point in robot's memory
def init_point(ser, name):
    serial_tools.send(ser, 'defp {}'.format(name))
    serial_tools.send(ser, 'here {}'.format(name))
    return Point(name=name)


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
def imgf_to_robf(point, p0, img_width, img_height, scale, rotate90):
    if rotate90 == 0:
        point.x = int((int(point.x) / img_width) * scale + int(p0.x))
        point.y = int((int(point.y) / img_height) * scale + int(p0.x))
    else:
        point.y = int((int(point.x) / img_width) * scale + int(p0.x))
        point.x = int((int(point.y) / img_height) * scale + int(p0.x))
    point.z = p0.z
    point.p = p0.p
    point.r = p0.r
    point.ptype = 'robot'

    return respects_boundaries(point)

def maxscale(img_width,img_height):
    
    x_max = 5000
    y_max = 3000
    
    x_scale = img_width/x_max
    y_scale = img_height/y_max
    
    return x_scale, y_scale

# function that change the coordinates x,y,z,p,r of a position pos relatively to P0
# '{}'.format(x) permet d'envoyer une valeur à la place de la variable au lieu d'un caractère
def set_point_coordinates(ser, point, p0, x=None, y=None, z=None, p=None, r=None):
    if x is not None: serial_tools.send(ser, 'setpvc {} X {}'.format(point.name, p0.x + x))
    if y is not None: serial_tools.send(ser, 'setpvc {} Y {}'.format(point.name, p0.y + y))
    if z is not None: serial_tools.send(ser, 'setpvc {} Z {}'.format(point.name, p0.z + z))
    if p is not None: serial_tools.send(ser, 'setpvc {} P {}'.format(point.name, p0.p + p))
    if r is not None: serial_tools.send(ser, 'setpvc {} R {}'.format(point.name, p0.r + r))


# function that move up and down pen at a given point relatively to P0
# todo: check if point has to be moved or just direct command
#           => modifying point coordinates may imply problem in memorized points
def moveup_pen(ser, p0, point, up):
    if up is True:
        set_point_coordinates(ser=ser, point=point, p0=p0, z=10)
        serial_tools.send(ser, 'move {}'.format(point.name))
    else:
        set_point_coordinates(ser=ser, point=point, p0=p0, z=-10)
        serial_tools.send(ser, 'move {}'.format(point.name))


# function that converts key points to a vector
def get_vector_from_keypoints(keypoints, p0, name, img_width, img_height, scale, rotate90):
    vect = Vector(name=name)
    vect.points = []
    reachability = 0
    for i in range(len(keypoints)):
        p = Point('p{}'.format(i), x=keypoints[i][0], y=keypoints[i][1])
        reachability |= imgf_to_robf(p, p0, img_width, img_height, scale, rotate90)
        vect.points.append(p)
    return vect, reachability


def respects_boundaries(point):
    x_max = 2970
    y_max = 2100
    return point.x < x_max and -y_max <= point.y <= y_max


def record_vector(ser, vector):
    dim = len(vector.points)
    # serial_tools.send(ser, 'DEFP {}'.format(vector.name))
    serial_tools.send(ser, 'DIMP {}[{}]'.format(vector.name, dim))
    c = 1
    for i in vector.points:
        if i.ptype == 'robot':
            # todo: check if command script is correct
            serial_tools.send(ser, 'HERE {}[{}]'.format(vector.name, c))
            serial_tools.send(ser, 'SETP {}[{}]=POSITION'.format(vector.name, c))
            serial_tools.send(ser, 'SETPVC {}[{}] X {}'.format(vector.name, c, vector.points[i].x))
            serial_tools.send(ser, 'SETPVC {}[{}] Y {}'.format(vector.name, c, vector.points[i].y))
            serial_tools.send(ser, 'SETPVC {}[{}] Z {}'.format(vector.name, c, vector.points[i].z))
            serial_tools.send(ser, 'SETPVC {}[{}] P {}'.format(vector.name, c, vector.points[i].p))
            serial_tools.send(ser, 'SETPVC {}[{}] R {}'.format(vector.name, c, vector.points[i].r))
            c += 1
        else:
            print('Error: points still in the image frame')
            exit(-1)


# function that allows to move the robot along the vector of position "vector" from the position 1 to n
def draw_vector(ser, vector):
    n = len(vector.points)
    serial_tools.send(ser, 'MOVES {} 1 {}'.format(vector.name, n), ask=1)


# function that allows to move the robot along the vector of position "vector" from the position 1 to n with a
# circular move
def draw_circ_vector(ser, vector):
    n = len(vector.points)
    for i in range(n):
        serial_tools.send(ser, 'TEACH {}[{}]'.format(vector.name, i+1), ask=1)
        serial_tools.send(ser, 'MOVEC {}[{}]'.format(vector.name, i+1))
        serial_tools.send(ser, 'HERE {}[{}]'.format(vector.name, i+1))
    serial_tools.send(ser, 'MOVEC {} 1 {}'.format(vector.name, n))
