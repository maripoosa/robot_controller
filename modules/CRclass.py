import queue
import threading

class CRclass():
    """This class is used to send requests or commans (accepted by the robot itself) between threads using queues.
    Beside commands and/or requests itself (stored as list of encoded strings (bytes type)) class contain information to which queue responses to the commands/requests shall be send. In addition it could be used to handle locks and condition (notifying thread wainting on alarm condition).
    Note that if requests/commands are stored as list they will be send in that exact order, with no possibility of other thread putting it's request/command 
    in order, as it could happen when sending requests/commands separetly. That being said It's not recommended to create long lists, because it would "block"
    process which reads this class contents. Class could instruct reading process to send all responses as list of strings or one by one as plain strings."""
    def __init__(self, cr, responseQ = None, lock = None, alarm = None, response_as_list = False):
        if type(cr) is type(str().encode()):
            self.cr = [ cr ]
        elif type(cr) is type([]):
            for i in range(0, len(cr)):
                if type(cr[i]) != type(str().encode()):
                    raise TypeError("element {} of passed list is not string".format(i))
            self.cr = cr
        else:
            raise TypeError("CR must be encoded string (bytes) or list of encoded strings, now is {}".format(type(cr)))
        
        if type(responseQ) is type(queue.SimpleQueue()) or type(responseQ) is type(queue.Queue()) or responseQ is None:
            self.responseQ = responseQ
        else:
            raise TypeError("responseQ must be SimpleQueue, Queue or None, is {}".format(type(responseQ)))
        
        if type(response_as_list) is type(bool()):
            self.response_as_list = response_as_list
        else:
            raise TypeError("response_as_list must be bool type not {}".format(type(response_as_list)))
        
        if type(lock) is type(threading.RLock()) and type(alarm) is type(threading.Condition()):
            self.lock = lock
            self.alarm = alarm
        elif lock is alarm is None:
            pass
        else:
            raise TypeError("Wrong lock and/or alarm types, lock is {}, alarm is {}".format(type(lock), type(alarm)))
        
        def wakeUp(self):
            """this method notifies thread that is waiting on alarm Condition and handles acquire/releaseing lock"""
            if self.lock is not None and self.alarm is not None:
                lock.acquire()
                alarm.notify()
                lock.release()
            else:
                raise RuntimeError("Lock and Condition is not specified")
