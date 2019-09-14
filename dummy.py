import socket
import sys
from modules import commands
from modules import requests
from modules import errors
import select

adc = [
        132,
        345,
        0,
        0,
        0,
        0,
        0,
        6000
        ]
srv = [
        123,
        123,
        123,
        123,
        123,
        123,
        123,
        123,
        123,
        123,
        123,
        123
        ]
    

def get(what):
    global adc
    global srv
    if what.startswith("adc".encode()):
        if what.endswith("?".encode()):
            return str(adc).encode()
        else:
            typ, number, qm = what.split()
            number = int(number)
            return str(adc[number]).encode()
    elif what.startswith("srv".encode()):
        if what.endswith("?".encode()):
            return str(srv).encode()
        else:
            typ, number, qm = what.split()
            number = int(number, 16)
            return str(srv[number]).encode()
    elif what == requests.ready():
        return str("y").encode()
    elif what == "ok ?":
        return "ok".encode()
    
class clientEX(Exception):
    def __init__(self, ex):
        self.ex = ex
 
    def __str__(self):
        return self.ex

class client:
    """client class for quadroped robot project"""
    def __init__(self, host, port):
        """initialize client"""
       
        self.__socket__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket__.connect((host, port))
        
        if self.__socket__.sendall("[R] Dummy".encode()) is not None:
            raise RuntimeError ("Can't contact the server")
   
    def connect(self, host, port):
        self.__socket__.connect((host, port))
 
    def send(self,msg):
        return self.__socket__.sendall(msg)
        
    def sendACK(self, msg, timeout=5):
        self.send(msg)
        ack = self.recevie(512)
        return ack
 
    def recevie(self, timeout=5):
        ready = select.select([self.__socket__], [], [], timeout)
        if ready[0]:
            msg = self.__socket__.recv(512)
        else:
            raise clientEX("response timeout")
        return msg
 
    def recevieACK(self, timeout = 5):
        msg = self.recevie(timeout)
        print(msg)
        print(msg[0:3])
        print(msg.endswith("?".encode()))
        if msg[0:3] in requests.requestList and msg.endswith("?".encode()):
            print(get(msg))
            self.send(get(msg))
            return None
        elif msg[0:3] in commands.commandList and not msg.endswith("?".encode()):
            self.send("ok".encode())
            return msg
        else: #command or request not recognized
            self.send(errors.badCR())
            return errors.badCR()
 
    def close(self):
        self.__socket__.close()

if __name__ == "__main__":
    cli = client("localhost", 8080)
    cli.recevie()
    while True:
        cli.recevieACK(None)
        for i in range(0, len(srv)):
            srv[i] = srv[i]+100
    cli.close()
