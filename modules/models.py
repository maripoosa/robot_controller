import pygame
import numpy as n
import math as m
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

class torso():
    """simplified (using box)  torso of the robot, initialized with its dimmensions in mm, and color as RGB tuple, values from 0 to 1 (full blue by default).
       Front of the robot will be marked by additional edge"""
    def __init__(self, width, height, length, color=(0,0,1)):
        self.__width__ = width
        self.__height__ = height
        self.__length__ = length
        self.color = color
        

        #define verticies. If we define them like this, body will be rendered in the center of coordinate system
        self.verticies = (
            (width/2, length/2, height/2),   #0
            (width/2, length/2, -height/2),  #1
            (width/2, -length/2, height/2),  #2
            (width/2, -length/2, -height/2), #3
            (-width/2, length/2, height/2),  #4
            (-width/2, length/2, -height/2), #5
            (-width/2, -length/2, height/2), #6
            (-width/2, -length/2, -height/2),#7
            )
      
        #edges of the torso
        self.edges = (
            (0,1),
            (0,2),
            (0,4),
            (3,1),
            (3,2),
            (3,7),
            (5,1),
            (5,4),
            (5,7),
            (6,2),
            (6,4),
            (6,7),
            (0,5), #front indicator
            (1,4)
            )
        self.edge_color = (1,1,1)
        #surfaces
        self.surfaces = (#surface:
            (0,1,5,4),   #front
            (0,2,3,1),   #right 
            (0,4,6,2),   #up
            (4,5,7,6),   #left
            (2,6,7,3),   #back
            (1,5,7,3)    #down
            )
    def Render(self):
        glBegin(GL_QUADS)
        for surface in self.surfaces:
            x = 0
            
            for vertex in surface:
                glColor3fv(self.color)
                glVertex3fv(self.verticies[vertex])
                x+=1
        glEnd()
        glBegin(GL_LINES)
        glColor3fv(self.edge_color)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
                        
        glEnd()

        
class leg():
    """leg class for robot, x,y,z are coordinates of mounting point of the leg in mm, l1,l2,l3 are segments lenghts in mm, T1,T2,T3 are angles expressed as an numerator of x/65535 fract
    and color is color in which leg is rendered""" 
    def __init__(self, x, y, z, T1=32767, T2=32767, T3=3276, l1=40, l2=60, l3=90, color=(1, 1, 0)):
        self.__x__=x 
        self.__y__=y
        self.__z__=z
        self.__l1__=l1
        self.__l2__=l2
        self.__l3__=l3
        self.color=color
        temp = self.__move__(T1, T2, T3)
        self.verticies = temp        
        
      
        #edges of the leg
        
        self.edges = (
            (0,1),
            (1,2),
            (2,3)
            )
            
            
        self.edge_color = color
    
        self.surfaces = () #leg has no surfaces

    def c(self, x):
        """cosinus fuction accepting 16Bit unsigned int as argument, note that servos have angle range from 0 to 180"""
        return m.cos(m.radians(180*x/65535))
                         
    def s(self, x):
        """sinus fuction accepting 16Bit unsigned int as argument, note that servos have angle range from 0 to 180"""
        return m.sin(m.radians(180*x/65535))

    def __move__(self, T1, T2, T3):
        """move the leg, returns tuple with positions of each segments"""
        Offset=n.array( [[1, 0, 0, self.__x__],
                         [0, 1, 0, self.__y__],
                         [0, 1, 1, self.__z__],
                         [0, 0, 0, 1         ]] )
        
        A1=n.array( [[self.c(T1), 0,     self.s(T1),  0          ],
                     [self.s(T1), 0,     -self.c(T1), 0          ],
                     [0,          1,     0,           self.__l1__],
                     [0,          0,     0,           1          ]] )
        
        A2=n.array( [[self.c(T2), -self.s(T2), 0,      self.__l2__*self.c(T2)],
                     [self.s(T2), self.c(T2),  0,      self.__l2__*self.s(T2)],
                     [0,          0,           1,      0                     ],
                     [0,          0,           0,      1                     ]] )

        A3=n.array( [[self.c(T3), -self.s(T3), 0,      self.__l3__*self.c(T3)],
                     [self.s(T3), self.c(T3),  0,      self.__l3__*self.s(T3)],
                     [0,          0,           1,      0                     ],
                     [0,          0,           0,      1                     ]] )

        T1=A1+Offset
        T2=A1.dot(A2)+Offset
        T3=A1.dot(A2.dot(A3))+Offset
        
        pos0 = (self.__x__, self.__y__, self.__z__)
        pos1 = (T1[0][3], T1[1][3], T1[2][3])
        pos2 = (T2[0][3], T2[1][3], T2[2][3])
        pos3 = (T3[0][3], T3[1][3], T3[2][3])
        
        return (pos0, pos1, pos2, pos3)
    
    def move(self, T1, T2, T3):
        self.verticies = self.__move__(T1, T2, T3)
        return self.verticies

    def Render(self):
        glBegin(GL_QUADS)
        for surface in self.surfaces:
            x = 0
            
            for vertex in surface:
                glColor3fv(self.color)
                glVertex3fv(self.verticies[vertex])
                x+=1
        glEnd()
        glBegin(GL_LINES)
        glColor3fv(self.edge_color)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
                        
        glEnd()


class QrobotModel():
    """model of robot with 4 legs, each leg has 3 segments, numerated from robot's body to ground"""
    def __init__(self, bodyDimmensions, startPosture, torsoColor=(0, 0, 1)):
        self.__startPosture__=startPosture
        self.torso = torso(bodyDimmensions[0], bodyDimmensions[1], bodyDimmensions[2], torsoColor)
        self.leg = (leg(bodyDimmensions[0]/2, bodyDimmensions[2]/2, bodyDimmensions[1]/2),
                    leg(-bodyDimmensions[0]/2, bodyDimmensions[2]/2, bodyDimmensions[1]/2),
                    leg(bodyDimmensions[0]/2, -bodyDimmensions[2]/2, bodyDimmensions[1]/2),
                    leg(-bodyDimmensions[0]/2, -bodyDimmensions[2]/2, bodyDimmensions[1]/2))
        for i in range(4):
            self.moveLeg(i, startPosture)
        self.__perspective__=0
        


    def moveLeg(self, number, T):
        """move leg to the T, where T is tuple containing all angles in natural coordinates"""
        if self.leg[number].__x__ < 0:
            off=-1
        else:
            off=1
        self.leg[number].move(T[0]*off, T[1], T[2])
        
    def Render(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.torso.Render()
        for i in range(4):
            self.leg[i].Render()
    def RotRender(self, a):
        glRotatef(a, 0, 0, 1 )
    

if __name__=='__main__':

    T1=200
    T2=3200
    T3=1600
    
    leg1=leg(40, 60, 20)
    """
    leg2=leg(-40, 60, 20)
    leg3=leg(40, -60, 20)
    leg4=leg(-40, -60, 20)
    body = torso(80, 40, 120)
    """
    r=QrobotModel((80, 40, 120), (16384, -12100, 40000))
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)

    gluPerspective(45, (display[0]/display[1]), 0.1, 1400.0)

    glTranslatef(0.0,0.0, -500)
   
    glRotatef(90, 2, 0, 0 )
    #glRotatef(90, 1, 0, 0)

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

       
        T1+=1000
        T2+=2000
        T3+=3000
        
        
        #leg1.Render()
        r.Render()
        r.moveLeg(0, (T1, 0, 0))
        r.moveLeg(1, (T1, 0, 0))
        r.moveLeg(2, (T1, 0, 0))
        r.moveLeg(3, (T1, 0, 0))
        
        #        leg1.move(16384, -12100, 40000)
        #leg1.move(T1, -12100, 40000)
        #leg2.move(T1, -12100, 40000)
        #leg3.move(T1, -12100, 40000)
        #leg4.move(T1, -12100, 40000)
        
        print(T1)
       # leg2.move(0, T3, 0)
       # leg3.move(0, 0, T3)
        #leg1.move(T1/4, T2/4, T3/4)
        #leg2.move(T1/3, T2/3, T3/3)
        #leg3.move(T1/2, T2/2, T3/2)
        #leg4.move(T1/1, T2/1, T3/1)
        glRotatef(2*m.sin(T1/1000000), 0, 0, 1);
        pygame.display.flip()
        pygame.time.wait(30)
