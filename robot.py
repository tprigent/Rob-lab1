import numpy
import tools

#function that change the coordinates x,y,z,p,r of a position pos relatively to P0
#'{0}'.format(x) permet d'envoyer une valeur à la place de la variable au lieu d'un caractère
def change(pos,x, y, z, p, r):
    tools.send(ser, 'teach pos')
    if x is not None tools.send(ser, 'setpvc pos X {0}'.format(x))
    if y is not None tools.send(ser, 'setpvc pos Y y')
    if z is not None tools.send(ser, 'setpvc pos Z z')
    if p is not None tools.send(ser, 'setpvc pos P p') 
    if r is not None tools.send(ser, 'setpvc pos R r')
    
#function that move up and down relatively to P0    
 def move_pen(pos, up):
    if up is true change(pos=pos,z=p0.z+10)
    else change(pos=pos, z=p0.z-10)
