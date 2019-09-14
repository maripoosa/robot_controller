#!/usr/bin/python

############################################################
#Imports
############################################################
import settings

from modules import *
from modules import commands as commands
from modules import requests as requests
from modules import errors as errors
from modules import reports as reports

import threading
import queue
from modules import CRclass as CR

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import os
import shutil

import ast

import time

############################################################
#Globals
############################################################

#objects used for storing servos data
servoList = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
servoList_lock = threading.RLock()

#adc readings
adcList = [ 0, 0, 0, 0, 0, 0, 0, 0 ]
adcList_lock = threading.RLock()

#escape flag
escape_lock = threading.RLock() 
escape = False

#keyboard flag, when false keyboard is not active
keyb = False
keyb_lock = threading.RLock()

#connection state objects
conn_lock = threading.RLock() #lock for variables below
conn = False
conn_state = "down"

#cli lock/condition classes
cli_lock = threading.RLock() #lock for cli condition obj
cli_alarm = threading.Condition(cli_lock)

#displayer lock/condition classes
disp_lock = threading.RLock()
disp_alarm = threading.Condition(disp_lock)

#Queues
toCliQ = queue.SimpleQueue() #Queue for sending data to client thread
toDispQ = queue.SimpleQueue() #Queue for sending data to displayer thread
toKeybQ = queue.SimpleQueue() #Queue for sending data to keyboardControl thread

#Functions used to control the robot
def resetPos():
    global toCliQ
 
    pack = [   
        commands.srv(0, 90, True),
        commands.srv(1, 90, True),
        commands.srv(2, 90, True), 
        commands.srv(3, 90, True),
     
        commands.srv(4, 90, True),
        commands.srv(5, 90, True),
        commands.srv(6, 90, True),
        commands.srv(7, 90, True),
     
        commands.srv(8, 90, True),
        commands.srv(9, 90, True),
        commands.srv(10, 90, True),
        commands.srv(11, 90, True),
        commands.ready(),
        ]
    toCliQ.put(CR.CRclass(pack))

############################################################
#Threads procedures
############################################################

def gui():
    global escape
    global escape_lock
    global toDispQ
    global disp_lock
    global disp_alarm
    
    #render rotate functions for button 9 and 10
    def renderRotCW():
        toDispQ.put(-4)
        disp_lock.acquire()
        disp_alarm.notify()
        disp_lock.release()
    
    def renderRotCCW():
        toDispQ.put(4)
        disp_lock.acquire()
        disp_alarm.notify()
        disp_lock.release()
    
    #movement functions
    def turnCW():
        """turn robot CW"""
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(CR.CRclass(commands.rotate("cw"))))
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
 
    def turnCCW():
        """turn robot CCW"""
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(commands.rotate("ccw")))
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
 
    def fwd():
        """one step forward"""
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(commands.step()))
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
 
    def left():
        """one step to the left"""
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(commands.step("left")))
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
    
    def right():
        """one step to the right"""
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(commands.step("right")))
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
    
    def back():
        """one step backward"""
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(commands.step("back")))
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
    
    def startPos():
        """set robot to starting position"""
        conn_lock.acquire()
        if conn == True:
            resetPos()
            cli_lock.acquire()
            cli_alarm.notify()
            cli_lock.release()
        conn_lock.release()
  
    #App state functions
    def keybSwitch():
        global keyb
        keyb = not keyb
 
    def connEnable():
        global conn
        global conn_lock
        conn_lock.acquire()
        if conn == False:
            resetPos()
        conn = not conn
        conn_lock.release()
        cli_lock.acquire()
        cli_alarm.notify()
        cli_lock.release()
    
    handlers = (
        turnCCW,
        fwd,
        turnCW,
        left,
        startPos,
        right,
        back,
        keybSwitch,
        renderRotCCW,
        renderRotCW,
        connEnable
        )
        
    
    builder = Gtk.Builder()
    builder.add_from_file("modules/panelcon.glade")
    builder.connect_signals(control.Handler(handlers))
    window = builder.get_object("window1")
    window.show_all()
    Gtk.main()
    
    escape_lock.acquire()
    escape = True
    escape_lock.release()
    cli_lock.acquire()
    cli_alarm.notify()
    cli_lock.release()
    return

def cli(host, port):
    """client thread procedure, sends, recieves and sorts data (by putting it to queues)"""
    global conn_state
    global conn_lock
    global conn
    global escape_lock
    global escape
    global cli_lock
    global cli_alarm
    global toCliQ
    global disp_lock
    global disp_alarm
    global toDispQ
    
    c = client.client(host, port)
     
    conn_lock.acquire()
    conn = True
    while True: #cli will work within loop until escape flag is true
        while conn == True: #note that conn might be modified outside the thread
            conn_lock.release()
            cli_lock.acquire()
            cli_alarm.wait()
            data = c.recevie(False) #recevie data which was not requested, nonblocking
            if len(data) is not 0:
                if data[0:3] in reports.reportsList: #if data is in correct form
                    toDispQ.put(data)
                    c.send("ok")
                else : #send error
                    c.send(errors.badCR())
            
            while toCliQ.empty() is False: #while there is available data in queue
                data = toCliQ.get()
                response=[]
                for msg  in data.cr: #for all commands/requests
                    ack=[]
                    for i in range(0, 5): #try to send one message  max 5 times, if fails raise exception
                        ack.append(c.sendACK(msg))
                        if ack[i] != errors.badCR():
                            break
                    if i == 4: #repeated 5 times with badCR error as response
                            raise RuntimeError ("Failed to send request, acknowlegments are {}".format(ack))
                    elif data.responseQ is not None: #sending thread wants response to this queue
                        if data.response_as_list is True: #as list, but can or want to wait until all messages have responses
                            response.append([msg, ack[i]])
                        else:
                            data.responseQ.put([msg, ack[i]]) #as strings, but ASAP
                            try:
                                data.wakeUp()
                            except:
                                pass
                if data.response_as_list is True:
                    data.responseQ.put(response)
                    try:
                        data.wakeUp()
                    except:
                        pass
                    
            cli_lock.release()
            #check escape flag
            escape_lock.acquire()
            if escape == True:
                escape_lock.release()
                c.close()
                return
            else:
                escape_lock.release()
            
            conn_lock.acquire()
        c.close()
        while conn == False: #wait for conn be true, note that conn could be modified outside the thread
            conn_lock.release()
            cli_lock.acquire()
            cli_alarm.wait()
            cli_lock.release()
            while toCliQ.empty() is False:
                toCliQ.get()
             #check escape flag
            escape_lock.acquire()
            if escape == True:
                escape_lock.release()
                return
            escape_lock.release()            
            conn_lock.acquire()
        c.reinit()

def displayer():
    """this thread displays robot and connection status data on console"""
    global conn_lock
    global conn
    global servoList_lock
    global servoList
    global disp_lock
    global disp_alarm
    global escape_lock
    global escape
    global adcList_lock
    global adcList
    
    robotModel = models.QrobotModel((100, 60, 100), (16384, -12100, 40000))
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)
 
    gluPerspective(45, (display[0]/display[1]), 0.1, 1400.0)
    glTranslatef(0.0,0.0, -500)
    glRotatef(90, 2, 0, 0 )
 
    robotModel.Render()
    pygame.display.flip()
    bcolors = {
        "HEADER" : '\033[95m',
        "OKBLUE" : '\033[94m',
        "OKGREEN" : '\033[92m',
        "WARNING" : '\033[93m',
        "FAIL" : '\033[91m',
        "ENDC" : '\033[0m',
        "BOLD" : '\033[1m',
        "UNDERLINE" : '\033[4m'
        }
 
    header = lambda s, n, c :  "{ss:{cs}^{ns}}".format(ss=s, ns=n, cs=c) #generates header string
    consoleRst = lambda : print("\033[0;0H")
    os.system("clear")
    minLines = 25 #minimal height of terminal required by displayer
    minColumns = 35 #minimal width of the terminal
    panel = 0 #this variable indicates what was last panel displayed, if other than one to be displayed then clear console first
    term_size = shutil.get_terminal_size()
    while True:
        disp_lock.acquire()
        disp_alarm.wait(0.15)
        disp_lock.release()
        #check escape flag
        escape_lock.acquire()
        if escape == True:
            escape_lock.release()
            break
        escape_lock.release()
        if term_size != shutil.get_terminal_size():
            term_size = shutil.get_terminal_size()
            os.system("clear")
        if term_size.lines > minLines and term_size.columns > minColumns :
            #get app status
            conn_lock.acquire()
            pconn = conn
            conn_lock.release()
            if pconn is True:
                strconn = bcolors.get("OKGREEN") + "connection: ok          "
            else:
                strconn = bcolors.get("WARNING") + "connection: disconnected"
            
            keyb_lock.acquire()
            pkeyb = keyb
            keyb_lock.release()
            if pkeyb is True:
                strkeyb = bcolors.get("OKGREEN") + "Keyboard enabled "
            else:
                strkeyb = bcolors.get("WARNING") + "Keyboard disabled"
         
            #get robot's status and change it's model
            if pconn is True:
                if panel != 1:
                    os.system("clear")
                    panel = 1
                while toDispQ.empty() == False:
                    r = toDispQ.get()
                    #resolve request type
                    if type(r) is type(int()):
                        robotModel.RotRender(r)
                        robotModel.Render()
                        pygame.display.flip()
                    #servos
                    elif r[0] == requests.srv(): #all
                        servoList_lock.acquire()
                        servoList = ast.literal_eval(r[1].decode("UTF-8")) #make list out of it's string representation
                        for i in range(0, 4):
                            robotModel.moveLeg(i, (servoList[i], servoList[i+4], servoList[i+8]))
                            robotModel.Render()
                            pygame.display.flip()
                        servoList_lock.release()
                    elif r[0][0:3] == requests.srv()[0:3]: #single
                        for i in range(0, 16):
                            if r[0] == requests.srv(i):
                                """
                                note that: 
                                servos with numbers from 0 to 3 are first segments of legs with numbers from 0 to 3 respectively,
                                servos with numbers from 4 to 7 are second segments of legs with numbers from 0 to 3 respectively
                                serwos with numbers from 8 to 11 are third segments of legs with numbers from 0 to 3 respectively
                                """
                                legNum = i % 4 
                                servoList_lock.acquire()
                                servoList[i] = int(r[1])
                                theta = (servoList[legNum], servoList[legNum+4], servoList[legNum+8])
                                robotModel.moveLeg(legNum, theta)
                                robotModel.Render()
                                pygame.display.flip()
                                servoList_lock.release()
                                break
                    #adc
                    elif r[0] == requests.adc(): #all
                        adcList_lock.acquire()
                        adcList = ast.literal_eval(r[1].decode("UTF-8"))
                        adcList_lock.release()
                    elif r[0][0:3] == requests.adc()[0:3]: #single
                        for i in range(0, 8):
                            if r[0] == requests.adc(i):
                                adcList_lock.acquire()
                                adcList[i] = int(r[1])
                                adcList_lock.release()
                    
                    consoleRst()
                    print(bcolors.get("BOLD") + header("App status", term_size.columns, '#') + bcolors.get("ENDC"))
                    print(strconn)
                    print(strkeyb + bcolors.get("ENDC"))
                    print(bcolors.get("BOLD") + header("Robot status", term_size.columns, '#') + bcolors.get("ENDC"))
                    
                    servoList_lock.acquire()
                    
                    for i in range(0, len(servoList)):
                        print("Servo {}: {:.2f} deg ({})".format(str(i).rjust(2), servoList[i]*180/(2**16), str(servoList[i]).ljust(5)))
                    servoList_lock.release()
                    adcList_lock.acquire()
                    for i in range(0, len(adcList)-1):
                        print("ADC {}: {}".format(i, str(adcList[i]).ljust(4)))
                    """
                    To calculate battery voltage we have to calculate ADC's quant and take voltagedividing ratio into account
                    """
                    Vbat = adcList[i+1] * (1.2/(2**10)) * (1.0/0.21) 
                    Vbat_color = bcolors.get("ENDC") #if battery voltage is below thresholds print it with normal color
                    if Vbat < 8.2: #battery critical
                        Vbat_color = bcolors.get("FAIL")
                    elif Vbat < 8.5: #battery low 
                        Vbat_color = bcolors.get("WARNING")
                    print("Vbat: {}{:.2f}V ({})".format(Vbat_color, Vbat, str(adcList[i+1])).ljust(4) + bcolors.get("ENDC"))
            else: #pconn is false
                if panel != 2:
                    os.system("clear")
                    panel = 2
                consoleRst()
                print(bcolors.get("BOLD") + header("App status", term_size.columns, '#') + bcolors.get("ENDC"))
                print(strconn)
                print(strkeyb + bcolors.get("ENDC"))
                print(bcolors.get("BOLD") + header("Robot status", term_size.columns, '#') + bcolors.get("ENDC"))
                print(bcolors.get("WARNING") + "Can't fetch robot status" + bcolors.get("ENDC"))
            
        else:
            os.system("clear")
            for i in range(0, term_size.lines//2 - 1):
                print("")
            print(bcolors.get("FAIL") + header("Terminal too small", term_size.columns, "!"))
            print(bcolors.get("ENDC"))
            panel = 0

def oscilator(period):
    """this thread is used to periodically send requests to robot,
    to, for example fetch sensor data"""
    global escape_lock
    global escape
    global conn_lock
    global conn
    global toCliQ
    global cli_lock
    global cli_alarm
    global disp_lock
    global disp_alarm
    global toDispQ
    global disp_lock
    global disp_alarm
    
    escape_lock.acquire()
    while escape == False: 
        escape_lock.release()
        time.sleep(period)
        conn_lock.acquire()
        if conn == True:
            toCliQ.put(CR.CRclass(requests.adc(), toDispQ, disp_lock, disp_alarm))
            toCliQ.put(CR.CRclass(requests.srv(), toDispQ, disp_lock, disp_alarm))
        else:
            disp_lock.acquire()
            disp_alarm.notify()
            disp_lock.release()
        conn_lock.release()
        cli_lock.acquire()
        cli_alarm.notify()
        cli_lock.release()
        escape_lock.acquire()
    escape_lock.release()
 
def keyboardControl():
    """this thread is responsible for keyboard control"""
    global escape_lock
    global escape
    global keyb_lock
    global keyb
    global toCliQ
    global toKeybQ
   
    pygame.init()
    escape_lock.acquire()
    while escape == False:
        escape_lock.release()
        pack = ["", requests.ready()]
        for event in pygame.event.get(): 
            keyb_lock.acquire()
            if event.type == pygame.KEYDOWN and keyb == True:
                keyb_lock.release()
                if event.key == pygame.K_w: #w
                    pack[0] = commands.step("backward")
                    toCliQ.put(CR.CRclass(pack, toKeybQ, None, None, True))
                    cli_lock.acquire()
                    cli_alarm.notify()
                    cli_lock.release()
                    rdy = False
                    while rdy is False:
                        for r in toKeybQ.get(): #this will block until cli return response
                            if r == [requests.ready(), reports.yes()]:
                                rdy = True
                                break
                        if rdy is True:
                            break
                        toCliQ.put(CR.CRclass(requests.ready(), toKeybQ, None, None, True))
                        cli_lock.acquire()
                        cli_alarm.notify()
                        cli_lock.release()
                        time.sleep(0.2)
                
                elif event.key == pygame.K_s: #s
                    pack[0] = commands.step("backward")
                    toCliQ.put(CR.CRclass(pack, toKeybQ, None, None, True))
                    cli_lock.acquire()
                    cli_alarm.notify()
                    cli_lock.release()
                    rdy = False
                    while rdy is False:
                        for r in toKeybQ.get(): #this will block until cli return response
                            if r == [requests.ready(), reports.yes()]:
                                rdy = True
                                break
                        if rdy is True:
                            break
                        toCliQ.put(CR.CRclass(requests.ready(), toKeybQ, None, None, True))
                        cli_lock.acquire()
                        cli_alarm.notify()
                        cli_lock.release()
                        time.sleep(0.2)
                
                elif event.key == pygame.K_a:
                    pack[0] = commands.step("left")
                    toCliQ.put(CR.CRclass(pack, toKeybQ, None, None, True))
                    cli_lock.acquire()
                    cli_alarm.notify()
                    cli_lock.release()
                    rdy = False
                    while rdy is False:
                        for r in toKeybQ.get(): #this will block until cli return response
                            if r == [requests.ready(), reports.yes()]:
                                rdy = True
                                break
                        if rdy is True:
                            break
                        toCliQ.put(CR.CRclass(requests.ready(), toKeybQ, None, None, True))
                        cli_lock.acquire()
                        cli_alarm.notify()
                        cli_lock.release()
                        time.sleep(0.2)
                
                elif event.key == pygame.K_d:
                    pack[0] = commands.step("right")
                    toCliQ.put(CR.CRclass(pack, toKeybQ, None, None, True))
                    cli_lock.acquire()
                    cli_alarm.notify()
                    cli_lock.release()
                    rdy = False
                    while rdy is False:
                        for r in toKeybQ.get(): #this will block until cli return response
                            if r == [requests.ready(), reports.yes()]:
                                rdy = True
                                break
                        if rdy is True:
                            break
                        toCliQ.put(CR.CRclass(requests.ready(), toKeybQ, None, None, True))
                        cli_lock.acquire()
                        cli_alarm.notify()
                        cli_lock.release()
                        time.sleep(0.2)
                
                elif event.key == pygame.K_q:
                    pack[0] = commands.rotate("ccw")
                    toCliQ.put(CR.CRclass(pack, toKeybQ, None, None, True))
                    cli_lock.acquire()
                    cli_alarm.notify()
                    cli_lock.release()
                    rdy = False
                    while rdy is False:
                        for r in toKeybQ.get(): #this will block until cli return response
                            if r == [requests.ready(), reports.yes()]:
                                rdy = True
                                break
                        if rdy is True:
                            break
                        toCliQ.put(CR.CRclass(requests.ready(), toKeybQ, None, None, True))
                        cli_lock.acquire()
                        cli_alarm.notify()
                        cli_lock.release()
                        time.sleep(0.2)
                
                elif event.key == pygame.K_e:
                    pack[0] = commands.rotate("cw")
                    toCliQ.put(CR.CRclass(pack, toKeybQ, None, None, True))
                    cli_lock.acquire()
                    cli_alarm.notify()
                    cli_lock.release()
                    rdy = False
                    while rdy is False:
                        for r in toKeybQ.get(): #this will block until cli return response
                            if r == [requests.ready(), reports.yes()]:
                                rdy = True
                                break
                        if rdy is True:
                            break
                        toCliQ.put(CR.CRclass(requests.ready(), toKeybQ, None, None, True))
                        cli_lock.acquire()
                        cli_alarm.notify()
                        cli_lock.release()
                        time.sleep(0.2)
                
                elif event.key == pygame.K_j:
                    toDispQ.put(4)
                
                elif event.key == pygame.K_l:
                    toDispQ.put(-4)
                
            else:
                keyb_lock.release()
            
        escape_lock.acquire()
        time.sleep(0.1)
    escape_lock.release()


############################################################
#main
############################################################
if __name__=="__main__":
    tgui = threading.Thread(None, gui)
    tcli = threading.Thread(None, cli, cli, (settings.host, settings.port))
    tosc = threading.Thread(None, oscilator, oscilator, (0.2,))
    tkey = threading.Thread(None, keyboardControl)
    print(">>>>>>>>>>>>>>>>>>>>starting threads<<<<<<<<<<<<<<<<<<<<")
    tgui.start()
    tcli.start()
    tosc.start()
    tkey.start()
    resetPos()
    displayer()
    os.system("clear")
