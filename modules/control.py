#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

class Handler: #button hanlder
    def __init__(self, handlers=()):
        """initialize Handler class, button handlers should be passed as touple"""
        if len(handlers) < 11:
            raise RuntimeError("not enough button handlers")
        self.__handlers__ = handlers
    
    def on_window1_destroy(self, *args):
        Gtk.main_quit()

    def on_button1_pressed(self, button):
        """turn CW button"""
        self.__handlers__[0]()
        
    def on_button2_pressed(self, button):
        """up arrow button"""
        self.__handlers__[1]()
        
    def on_button3_pressed(self, button):
        """turn CCW button"""
        self.__handlers__[2]()
        
    def on_button4_pressed(self, button):
        """left arrow button"""
        self.__handlers__[3]()
        
    def on_button5_pressed(self, button):
        """start button """
        self.__handlers__[4]()
        
    def on_button6_pressed(self, button):
        """right arrow button"""
        self.__handlers__[5]()
        
    def on_button7_pressed(self, button):
        """down arrow button"""
        self.__handlers__[6]()
        
    def on_button8_pressed(self, button):
        """kebB button"""
        self.__handlers__[7]()

    def on_lock_pressed(self, button):
        """disc button"""
        self.__handlers__[10]()
        
    def on_button9_pressed(self, button):
        """rotate camera CCW"""
        self.__handlers__[8]()
        
    def on_button10_pressed(self, button):
        """rotate camera CW"""
        self.__handlers__[9]()
        
    def on_button11_pressed(self, button):
        """esc button"""
        Gtk.main_quit()


if __name__ == '__main__':
    import models 
    r=models.QrobotModel((100, 60, 100), (16384, -12100, 40000))
    builder = Gtk.Builder()
    builder.add_from_file("panelcon.glade")
    builder.connect_signals(Handler())
    
    window = builder.get_object("window1")
    window.show_all()
    
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)

    gluPerspective(45, (display[0]/display[1]), 0.1, 1400.0)

    glTranslatef(0.0,0.0, -500)
   
    glRotatef(90, 2, 0, 0 )

    r.Render()
    pygame.display.flip()
    clear()
    Gtk.main()
        
        
