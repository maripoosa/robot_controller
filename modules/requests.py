"""this file contains functions used to generate requests which are acceptable by the robot and exceptions for these functions"""
#exceptions
class adcEX(Exception):
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return self.ex

class ServoEX(Exception):
    """exception raised when something goes wrong with the servo"""
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return self.ex

#functions
def srv(n="all"):
    """generates request which will cause robot to send n servo position, or all servo position"""
    if n == "all":
        return "srv ?".encode()
    if n not in range(0, 16):
        raise ServoEX("There is no servo with number {}".format(n))
    else:
        servoNum = "%X" %int(n)
    return ("srv " + str(servoNum) + "?").encode()

def GroundSensor():
    """generates which will cause robot to send ground sensors state (as an 8 bit mask)"""
    return "gsr ?".encode()

def adc(n="all"):
    """generates request which will cause robot to send value of n channel of adc"""
    if n == "all":
        return "adc ?".encode()

    if n in range(0, 8):
        return ("adc " + str(n) + "?").encode()
    else:
        raise adcEX("ADC does not have {} channel".format(n))

def battery_level():
    """generates request which would cause robot to return value of adc channel which is connected to bettery probe"""
    return adc(7)

def ready():
    """generates request which will cause robot's report about finishing tasks. The diffrence between ready request and ready command is that command will cause robot to send 'ok' message AFTER it finishes all his tasks and request will resault in y/n response immediately"""
    return "rdy ?".encode()

def ok():
    """generates request which causes robot to send "ok" message, can be used to test connection"""
    return "ok ?".encode()

############################################################
#lists
############################################################
requestList = {
    "srv".encode(),
    "adc".encode(),
    "gsr".encode(),
    "rdy".encode(),
    "ok".encode()
    }
    
    

if __name__ == '__main__':
    print(srv(11))
    print(adc(3))
    print(battery_level())
    print(ok())
    
