"""this file contains functions which generate error messages"""
def badCR():
    """command or request is not recognized"""
    return "err badCR".encode()

def servoRange(n):
    """command tried to set angle of n servo out of its range"""
    servoNum = "%X" %int(n)
    return ("err srv{} range".format(n)).encode()

def servoNum(n):
    """servo which was requested does not exists"""
    Num = "%X" %int(n)
    return ("err srv{} doesn't exist".format(Num)).encode()

def adcNum(n):
    """adc channel number n does not exist"""
    return ("err adc{} doesn't exist".format(n)).encode()

def timeOut():
    return "err timeout".encode()

