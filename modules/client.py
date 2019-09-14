import socket
import sys
from . import commands
from . import requests
from . import errors
import select

class clientEX(Exception):
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return self.ex

class client:
    """client class for quadroped robot project"""
    def __init__(self, host, port):
        """initialize client"""
        self.__host__ = host
        self.__port__ = port
        self.__socket__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connect__(host, port)
        self.__socket__.setblocking(False)
    
    def __connect__(self, host, port):
        self.__socket__.connect((host, port))
        self.state = "up"
        if self.__socket__.sendall("[C] Webapp controler".encode()) is not None:
            raise RuntimeError ("Can't contact the server")
        response = self.recevie(True)
        if response != "ok".encode():
            raise clientEX("wrong response to the handshake, server response {}".format(response))
 
    def reinit(self, host=None, port=None):
        if host is None:
            host = self.__host__
        if port is None:
            port = self.__port__
        self.__init__(host, port)
    
    def send(self,msg):
        self.__socket__.sendall(msg)
 
    def sendACK(self, msg, timeout = None):
        """sends message, waits for acknowlegment and returns it"""
        self.send(msg)
        ack = self.recevie(True, timeout)
        return ack
 
    def recevie(self, blocking = True, timeout = None):
        """recevies data from socket if available, can block if timeout (in seconds) is 0 or less"""
        if blocking == True:
            ready = select.select([self.__socket__], [], [], timeout)
            if ready[0]:
                msg = self.__socket__.recv(512)
            else:
                raise clientEX("response timeout")
            return msg
        else:
            try:
                return self.__socket__.recv(512)
            except:
                return "".encode()

    def is_data(self, timeout = None):
        """checks if there is data to recieve from the socket, if there is, returns true, false otherwise"""
        return select.select([self.__socket__], [], [], timeout)
    
    def close(self):
        self.state = "down"
        self.__socket__.close()

if __name__ == "__main__":
    cli = client("localhost", 80)
    msg="uiadshiusdh".encode()
    msg = cli.sendACK(msg, 10000)
    print (msg)
    cli.close()
