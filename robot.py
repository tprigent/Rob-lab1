import numpy
import re
import serial_tools


class Point:
    def __init__(self, name='point', ptype='robot', x=0, y=0, z=0, p=0, r=0):
        self.name = name
        self.ptype = ptype
        self.x = x
        self.y = y
        self.z = z
        self.p = p
        self.r = r

    def print_point(self):
        print('\n### POINT {} coordinates (in {}) ###'.format(self.name, self.ptype))
        print('X={}  Y={}  Z={}  P={}  Z={}'.format(self.x, self.y, self.z, self.p, self.r))


# create a point in robot's memory
def init_point(ser, name):
    serial_tools.send(ser, 'defp {}'.format(name))
    serial_tools.send(ser, 'here {}'.format(name))
    return Point(name=name)


# fills Point instance with robot memory data
# todo: to be tested
def get_point_coordinates(ser=None, point=None):

    # get point info from robot
    response = serial_tools.send(ser, 'listpv {}'.format(point.name))

    # run regex to extract coordinates
    regex = r"(?:X|Y|Z|P|R):.-?[0-9]*"
    coordinates = re.finditer(regex, response, re.MULTILINE)

    # fill Point structure
    i = 0
    for c in coordinates:
        coord = c.group().split(":", 1)[1]
        if i == 0:   point.x = coord
        elif i == 1: point.y = coord
        elif i == 2: point.z = coord
        elif i == 3: point.p = coord
        elif i == 4: point.r = coord
        i += 1

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
