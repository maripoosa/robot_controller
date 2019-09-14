#!/usr/bin/python
import socket
import sys
import select
import fileinput
import datetime
import time
import settings

class serv:
    """Server class for quadroped robot project"""
    def __init__(self, host, port, log_create=False):
        """initialize server by creating and binding socket and then litsening for connections and accepting them"""
        #creating log file
        now = datetime.datetime.now()
        timestamp = str(now.year) + "." \
        + str(now.month) + "."\
        + str(now.day) + "."\
        + str(now.hour) + "."\
        + str(now.minute) + "."\
        + str(now.second)
        if log_create is True:
            self.__log_file__ = open( "logs/log" + timestamp, 'w')
        else:
            self.__log_file__ = None
        
        try:
            self.__sock__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err_msg:
            raise Exception('Unable to instantiate socket. Error code: ' + str(err_msg[0]) + ' , Error message : ' + err_msg[1])
        self.__sock__.bind((host,port))
        self.printNLog ("waiting for connections")
        self.__sock__.listen(2)
        
        socka, ipa=self.__sock__.accept()
        self.printNLog ("connection established - IP:  " +str (ipa))
        namea, addr = socka.recvfrom(512);
        namea = namea.decode('UTF-8')
        self.printNLog("device reported name: " + str(namea) )
        
        sockb, ipb=self.__sock__.accept()
        self.printNLog ("connection established - IP:  " +str (ipb))
        nameb, addr = sockb.recvfrom(512);
        nameb = nameb.decode('UTF-8')
        self.printNLog("device reported name: " + str(nameb))
        
    
        self.__robot_soc__= None
        self.__app_soc__= None
        #solve devices purpose
        if namea[0:3] == "[C]":
            self.__app_soc__ = socka
        elif namea[0:3] == "[R]":
            self.__robot_soc__ =socka
            
        if nameb[0:3] == "[C]":
            self.__app_soc__ = sockb
        elif nameb[0:3] == "[R]":
            self.__robot_soc__ =sockb
            
        #check if there is an controller and robot
        if self.__robot_soc__== None:
            self.printNLog("robot not connected!:<")
            self.close()
            return
        if self.__app_soc__ == None:
            self.printNLog("There are no controllers connected")
            self.close()
            return
        #send info to clients that they can start working
        
        self.__app_soc__.send("ok".encode())
        self.__robot_soc__.send("ok".encode())
        
    
    def __restore_connection__(self):
        """restores connection with previously closed socket by waiting for missing endpoint type to connect again"""
        while True:
            self.__sock__.listen(1)
            socka, ipa=self.__sock__.accept()
            self.printNLog ("connection established - IP:  " + str(ipa))
            namea, addr = socka.recvfrom(512);
            namea = namea.decode('UTF-8')
            self.printNLog("device reported name: " + str(namea) )
            #solve devices purpose
            if namea[0:3] == "[C]" and self.__app_soc__ == None: #if lost connection with client
                socka.sendall("ok".encode())
                return socka, namea[0:3]
            elif namea[0:3] == "[R]" and self.__robot_soc__ == None: #if lost connection with robot
                socka.sendall("ok".encode())
                return socka, namea[0:3]
            else:
                socka.close()
                self.printNLog("wrong endpoint, retrying ...")
    
    def reinit(self, host, port):
        """reinitialize server"""
        self.__init__(host, port)
 
    def loop(self):
        """main loop of the server, note that it is not final version of the serwer, in future additional features will be implemented"""
        if self.__robot_soc__ == None or self.__app_soc__ == None:
            self.printNLog("some of endpoints not connected, exiting main loop")
            return -1
        self.printNLog("Working, press E to exit")
        work = True
        while work == True:
            state = select.select(
                [self.__app_soc__, self.__robot_soc__, sys.stdin], #checks if there is data to recieve from the sockets or stdin
                [],
                [self.__app_soc__, self.__robot_soc__]) #cheks for sockets errors 
         
            if len(state[2]) is not 0: #error in any socket, note that state is tuple containing lists which are containing sockets
                for i in range(0, len(state[2])):
                    self.printNLog ("error in {}".state[2][i])
                    if state[2][i] == self.__app_soc__:
                        self.printNLog("Application socket error")
                    else:
                        self.printNLog("Robot socket error")
                    self.printNLog("Closing broken connettion")
                    state[2][i].close()
                    state[2][i] = None
                self.printNLog("Attempting to reconnect")
                for i in range(0, len(state[2])):
                    temp_sock, temp_type = self.__restore_connection__()
                    if temp_type == "[R]":
                        self.__robot_soc__ = temp_sock
                    else:
                        self.__app_soc__ = temp_sock
         
            if len(state[0]) is not 0: #there is data to recieve on one of the sockets or data to read from stdin
                for i in range(0, len(state[0])):
                    if state[0][i] is self.__app_soc__:
                        data = self.__app_soc__.recv(512)
                        if len(data) == 0: #socket disconnected
                            self.printNLog("Controller disconnected")
                            self.__app_soc__.close()
                            self.__app_soc__ = None
                            self.printNLog("Attempting to reconnect")
                            self.__app_soc__, name = self.__restore_connection__()
                        else:
                            try:
                                self.__robot_soc__.sendall(data)
                                self.printNLog("[C] -> [R]: " + str(data)) #print output of controller
                            except Exception as e:
                                #if this happens then it means that socket was allright just a while ago
                                self.printNLog("Error in robot socket (right before sending data): {}".format(e))
                    elif state[0][i] is self.__robot_soc__:
                        data = self.__robot_soc__.recv(512)
                        if len(data) == 0: #socket disconnected
                            self.printNLog("Robot disconnected")
                            self.__robot_soc__.close()
                            self.__robot_soc__ = None
                            self.printNLog("Attempting to reconnect")
                            self.__robot_soc__, name = self.__restore_connection__()
                        else:
                            try:
                                self.__app_soc__.sendall(data)
                                self.printNLog("[R] -> [C]: " + str(data)) #print output of controller
                            except Exception as e:
                                #if this happens then it means that socket was allright just a while ago
                                self.printNLog("Error in app socket (right before sending data): {}".format(e))
                    elif state[0][i] is sys.stdin: #read data from stdin
                        exit_command = (
                            "e",
                            "ex",
                            "exit"
                        )
                        for line in fileinput.input():
                            line = "".join(line.split())
                            self.printNLog("End of the session")
                            if line.lower() in exit_command:
                                work = False
                            fileinput.close()
                            break
                            
            
        return 0
 
    def close(self):
        if self.__robot_soc__ is not None:
            self.__robot_soc__.close()
        if self.__app_soc__ is not None:
            self.__app_soc__.close()
        self.__sock__.shutdown(socket.SHUT_RDWR)
        self.__sock__.close()
        self.__log_file__.close()
 
    def printNLog(self, string, log_write = None):
        print(string)
        if self.__log_file__ is not None:
            self.__log_file__.write(string + "\n")
        
if __name__ == "__main__":
    print ("server listening on {} port {}".format(socket.gethostbyname(socket.gethostname()), settings.port))
    serwer = serv(socket.gethostbyname(socket.gethostname()), settings.port, True) #server on this machine address and port from settings file
    
    serwer.loop()
    serwer.close()
    
