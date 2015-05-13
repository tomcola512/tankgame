from twisted.spread import pb
from twisted.internet import reactor
from twisted.python import util
import sys

class EchoClient(object):
    def connect(self):
        clientfactory = pb.PBClientFactory()
        reactor.connectTCP("localhost", 8789, clientfactory)
        self.d = clientfactory.getRootObject()
        self.d.addCallbacks(self.got_obj, self.err_obj)
        
    def got_obj(self, obj):
        print "got object: ", obj
        self.server = obj
        print "going to input call"
        #def2 = self.server.callRemote("add", 1, 2)
        #def2.addCallbacks(self.add_done, self.err)
        input_call()
        
    def err_obj(self, reason):
        print "error getting object: ", reason
        self.quit()
        
        
    def err(self, reason):
        print "error running remote method: ", reason
        self.quit()
        
    def quit(self):
        print "shutting down"
        reactor.stop()
        
    def req_add(self, a, b):
        d = self.server.callRemote("add", int(a), int(b))
        d.addCallbacks(recv_add, self.err)
        
    def req_sub(self, a, b):
        d = self.server.callRemote("subtract", int(a), int(b))
        d.addCallbacks(recv_sub, self.err)
    
    def req_echo(self, str):
        d = self.server.callRemote("echo", str)
        d.addCallbacks(recv_echo, self.err)

def recv_add(result):
    print "Sum is: "
    print result
    input_call()

def recv_sub(result):
    print "Difference is: "
    print result
    input_call()

def recv_echo(result):
    print "Server echoed: "
    print result
    input_call()

def input_call():
    print "select mode (1=add, 2=sub, 3=echo, q=quit)"
    try:
        print conn.server
    except:
        print "Not connected"
    mode = raw_input('mode: ')
    if mode == '1':
        print "input two numbers to add"
        a = raw_input('a: ')
        b = raw_input('b: ')
        conn.req_add(a, b)
    elif mode == '2':
        print "input two numbers to subtract"
        a = raw_input('a: ')
        b = raw_input('b: ')
        conn.req_sub(a, b)
    elif mode == '3':
        print "input string to echo"
        str = raw_input('str: ')
        conn.req_echo(str)
    elif mode == 'q':
        conn.quit()
    else:
        input_call()
    
conn = None
if __name__ == '__main__':
    conn = EchoClient()
    conn.connect()
    reactor.run()
    
    