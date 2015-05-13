from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import time
import random

class ServerObject(pb.Root):
    def __init__(self):
        self.started_at = int(round(time.time() * 1000))
        self.last_update = self.started_at
    def remote_add(self, one, two):
        answer = int(one) + int(two)
        print "returning result:", answer
        return answer
    def remote_subtract(self, one, two):
        return one - two
        
    def echo(self):
        return None
        
    def remote_echo(self, foo):
        global seq
        seq=seq+1
        print 
        print "Echoing \"" + str(foo) + " | " + str(seq)
        time.sleep(random.random())
        return foo
        
    def update_state(self):
        new_time = int(round(time.time() * 1000))
        ms = new_time - self.last_update
        
        #update game state
        
        self.last_update = new_time
seq = 0
if __name__ == '__main__':
    server = ServerObject()
    reactor.listenTCP(8789, pb.PBServerFactory(server))
    lc = LoopingCall(server.update_state)
    lc.start(1.0/120)
    reactor.run()