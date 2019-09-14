"""This file contains reports returned by robot other than values (if for example "adc ?" request is send, response would be send as list containing values of each adc)"""

def yes():
    return "y".encode()

def no():
    return "n".encode()

############################################################
#List
############################################################
reportsList = [
    "yes".encode(),
    "no".encode()
    ]
