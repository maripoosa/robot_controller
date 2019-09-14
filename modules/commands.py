"""this file contains functions and objects used to generate commands which are acceptable by the robot and exceptions for these functions"""
#exceptions
class ServoEX(Exception):
    """exception raised when something goes wrong with the servo"""
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return self.ex

class UsrDataEX(Exception):
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return self.ex

class StepEX(Exception):
    def __init__(self, ex):
        self.ex = ex
    def __str__(self):
        return self.ex

#functions    
def srv(n, angle, in_deg=False):
    """sets angle of servo number n to the specified value, command format : srv <n> <value>,
    where n is number of serwo (hexadecimal), value is angle in 16 bit uint format """
    if n not in range(0, 16):
        raise ServoEX("There is no servo with number {}".format(n))
    else:
        servoNum = "%X" %int(n)
    if in_deg == False: #angle is expressed as 16 bit int
        if angle not in range(0, 2**16):
            raise ServoEX("Servo angle {} (in 16 bit int format) out of range!".format(angle))
        else:
            sendAngle = int(angle)
    else : #angle expressed in degrees
        if angle not in range(0, 180):
            raise ServoEX("Servo angle {} degrees is out of range!".format(angle))
        else:
            sendAngle = int(angle/180*2**16) #convert angle to the int format accepted by the robot
    return ("srv " + servoNum + " " + str(sendAngle)).encode()

def usr(data):
    """send user defined data, divide it to packets of maximum 32 bits (including prefix)"""
    if type(data) is not str:
        try:
            data=str(data);
        except:
            raise UsrDataEX("User data must be convertable to string, and {} type is not".format(type(data)))
    n=32-len("usr ")
    packets = [data[i:i+n].encode() for i in range(0, len(data), n)]
    return packets

def step(direction="forward"):
    """generate step command"""
    direction={
        "f" : "f",
        "F" : "f",
        "b" : "b",
        "B" : "b",
        "l" : "l",
        "L" : "l",
        "r" : "r",
        "R" : "r"
        }.get(direction[0], None)
    if direction is not None:
        return ("stp " + direction).encode()
    else:
        raise StepEX("wrong direction")

def rotate(direction):
    """generate command which will cause robot to turn"""
    direction={
        "cw" : "cw",
        "CW" : "cw",
        "CCW" : "ccw",
        "ccw" : "ccw"
        }.get(direction, None)
    if direction is not None:
        return ("rot " + direction).encode()
    else:
        raise StepEX("wrong direction in rotation")

def buzz(freq, time):
    """generates command which will cause robot to beep, frequency in Hz, time in ms"""
    freq = int(freq) #convert input to ints
    time = int(time)
    return ("buz " + str(freq) + " " + str(time)).encode()

def ready():
    """generates command which will cause robot to report when it is ready (after it finishes all commands)"""
    return "rdy".encode()

def ok():
    """generates ok respone"""
    return "ok".encode()

############################################################
#lists
############################################################
commandList = {
    "srv".encode(),
    "stp".encode(),
    "rot".encode(),
    "buz".encode(),
    "rdy".encode(),
    "usr".encode()
    }
    



if __name__ == '__main__':
    print (srv(12, 30, True))
    print (usr("abcdefghijklmnopqrstuvwxyz 0123456789")) #this will be divided into two blocks
    print (step("F"))
    print (rotate("CCW"))
    print (buzz(1000, 3000))


