from . import models
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

if __name__=='__main__':
    r=models.QrobotModel((80, 40, 120), (16384, -12100, 40000))
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)

    gluPerspective(45, (display[0]/display[1]), 0.1, 1400.0)

    glTranslatef(0.0,0.0, -500)
   
    glRotatef(90, 2, 0, 0 )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        r.Render()
        com=input(">>>")
        if com[0:3] == "srv":
            #get the number of serwo, if not valid number return -1
            num={
                "1" : 1,
                "2" : 2,
                "3" : 3,
                "4" : 4,
                "5" : 5,
                "6" : 6,
                "7" : 7,
                "8" : 8,
                "9" : 9,
                "A" : 10,
                "B" : 11,
                "C" : 12
                }.get(com[3], -1)
            value = int(com[5:])
            print("serwo nr {} value {}".format(num,value))
        else:
            print("error")

        T1=0;
        T2=0;
        T3=0;
        leg_number = num%4
        if num in range(4):
            T1=value
        if num in range(4, 8):
            T2=value
        if num in range(8, 12):
            T3=value

        r.moveLeg(leg_number, (T1, T2, T3))
        r.Render()
        pygame.display.flip()
        
        
