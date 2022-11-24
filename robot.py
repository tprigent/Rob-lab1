import numpy
import tools


class Point:
    def __init__(self):
        self.name = 'pos'
        self.x = 0
        self.y = 0
        self.z = 0
        self.p = 0
        self.r = 0


# function that change the coordinates x,y,z,p,r of a position pos relatively to P0
# '{}'.format(x) permet d'envoyer une valeur à la place de la variable au lieu d'un caractère
def change(ser, pos, p0, x, y, z, p, r):
    tools.send(ser, 'teach {}'.format(pos))
    if x is not None: tools.send(ser, 'setpvc {} X {}'.format(pos, p0.x + x))
    if y is not None: tools.send(ser, 'setpvc {} Y {}'.format(pos, p0.y + y))
    if z is not None: tools.send(ser, 'setpvc {} Z {}'.format(pos, p0.z + z))
    if p is not None: tools.send(ser, 'setpvc {} P {}'.format(pos, p0.p + p))
    if r is not None: tools.send(ser, 'setpvc {} R {}'.format(pos, p0.r + r))


# function that move up and down relatively to P0
def move_pen(ser, p0, pos, up):
    if up is True:
        change(ser=ser, pos=pos, p0=p0, x=None, y=None, z=p0.z + 10, p=None, r=None)
    else:
        change(ser=ser, pos=pos, p0=p0, x=None, y=None, z=p0.z - 10, p=None, r=None)
