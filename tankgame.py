#networking reference http://ezide.com/games/writing-games.html
import pygame
from pygame.locals import *
import pygame._view # for py2exe
from math import cos
from math import sin
from math import pi
import random

from twisted.spread import pb
from twisted.internet import reactor, threads
from twisted.python import util
from twisted.internet.task import LoopingCall
from client import EchoClient

pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()


#sound array reference 
# http://pygame-catalin.blogspot.com/2014/12/pygame-using-sound-mixer-volume.html

pygame.mixer.init()
pygame.mixer.set_num_channels(128)

sounds = {}
sounds['pew'] = pygame.mixer.Sound('pew.ogg')
sounds['pew2'] = pygame.mixer.Sound('pew2.ogg')
sounds['pew'].set_volume(.0001)

sounds['beep'] = pygame.mixer.Sound('beep.ogg')
sounds['pew'].set_volume(.3)
sounds['engine'] = pygame.mixer.Sound('engine.ogg')
sounds['whine'] = pygame.mixer.Sound('whine.ogg')
sounds['whine'].set_volume(.3)

width = 800
height = 600
size = [width, height]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("TANK GAME")

clock = pygame.time.Clock()

v2 = pygame.math.Vector2
ms = 0
lms = 0
seq = 0
def timescale(x):
    return x*lms/1000.0

def rotate(offset, center, angle):
    x = offset[0]
    y = offset[1]
    return (center[0] +  x*cos(angle) - y*sin(angle), center[1] + x*sin(angle) + y*cos(angle))
    
def squarefy(width, height):
    return [(-width/2, -height/2),
    (width/2, -height/2),
    (width/2, height/2),
    (-width/2, height/2)]
    
def blit_alpha(target, source, location, opacity):
    x, y = location
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)
    
class EchoClient(object):
    def __init__(self):
        self.server = None
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
        tick_begin()
        
    def err_obj(self, reason):
        #print "error getting object: ", reason
        print "Could not connect to server!"
        print "starting single player ..."
        single_player()
        
        
    def err(self, reason):
        print "error running remote method: ", reason
        self.quit()
        
    def quit(self):
        print "shutting down"
        if self.server:
            reactor.stop()
        self.server = None
    '''
    def req_add(self, a, b):
        d = self.server.callRemote("add", int(a), int(b))
        d.addCallbacks(recv_add, self.err)
        
    def req_sub(self, a, b):
        d = self.server.callRemote("subtract", int(a), int(b))
        d.addCallbacks(recv_sub, self.err)
    '''
    def req_echo(self, str):
        if not inputs['done']:
            d = self.server.callRemote("echo", str)
            #d.addCallbacks(self.got_echo, self.err)
            cb = lambda x: reactor.callFromThread(tick_return, x)
            d.addCallbacks(cb, self.err)
            
    def got_echo(self, response):
        print "GOT " + response
        return response
    
class Proj:
    def __init__(self, pos, dir, speed, length, creator=None):
        self.pos = pos
        self.dir = dir
        self.creator = creator
        self.speed = speed
        self.length = length
    def move(self):
        self.dir += timescale((random.random()/60)-(1.0/120))
        self.pos = rotate((0, -timescale(self.speed)), self.pos, self.dir)
    def draw(self):
        pos2 = rotate((0, self.length), self.pos, self.dir)
        pygame.draw.line(screen, (255, 255, 255), self.pos, pos2, 2)
        
class Spark:
    def __init__(self, pos, dir, speed, born, ttl):
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.born = born
        self.ttl = ttl
    def alive(self):
        return pygame.time.get_ticks() < self.born + self.ttl
    
    def move(self):
        self.dir += timescale((random.random()/12)-(1.0/24))
        self.pos = rotate((0, -timescale(self.speed)), self.pos, self.dir)
    
    def draw(self):
        alpha = 255 - int((pygame.time.get_ticks() - self.born) * 255.0 / 120)
        pos = rotate((0, -4), (5,5), self.dir)
        pos2 = rotate((0, 4), (5,5), self.dir)
        scratch = pygame.Surface((9, 9), pygame.SRCALPHA)
        pygame.draw.line(scratch, (255, 255, 100), pos, pos2)
        blit_alpha(screen, scratch, (self.pos[0]-2, self.pos[1]-2), alpha)
        
    
class Tank:
    speed = 90
    width = 30
    height = 40
    cwidth = 10
    cheight = 30
    
    def __init__(self, pos, dir, candir, ammo, cooldown):
        self.pos = pos
        self.dir = dir
        self.candir = candir
        self.ammo = ammo
        self.cooldown = cooldown
        
        self.last_shot = None
    
    def fire(self):
        now = pygame.time.get_ticks()
        if not self.last_shot or now >= self.last_shot + self.cooldown:
            self.last_shot = now
            pos = rotate((0, -self.cheight/2 - 6), self.pos, self.candir)
            p = Proj(pos, self.candir, 480, 6, self)
            proj.append(p)
            
            sounds['pew'].play()
            sounds['pew2'].play()
            
            for x in xrange(8):
                dir = self.candir+(2*random.random())-1
                speed = 240 + random.random()*480
                offset = random.random()*self.cwidth/4.0-(self.cwidth/8.0)
                rightdir = self.candir + pi/2
                
                pos2 = rotate((0, -offset), self.pos, rightdir)
                pos2 = rotate((0, -18), pos2, self.candir)
                
                sparks.append(Spark(pos2, dir, speed, now, speed))
            
            return True
        return False
    
    def move(self):
        self.pos = rotate((0, -timescale(self.speed)), self.pos, self.dir)
    def reverse(self):
        self.pos = rotate((0, timescale(self.speed*.4)), self.pos, self.dir)
    def draw(self):
        
        
        tankpoly = squarefy(self.width, self.height)
        tankrot = lambda x: rotate(x, self.pos, self.dir)
        tankpoly = map(tankrot, tankpoly)
        
        cannpoly = squarefy(self.cwidth, self.cheight)
        cannrot = lambda x: rotate(x, self.pos, self.candir)
        cannpoly = map(cannrot, cannpoly)
        
        lefttrack = [(-self.width/2, -self.height/2),
            (-self.width/3, -self.height/2),
            (-self.width/3, self.height/2),
            (-self.width/2, self.height/2)]
        
        lefttrack = map(tankrot, lefttrack)
        
        righttrack = [(self.width/3, -self.height/2),
            (self.width/2, -self.height/2),
            (self.width/2, self.height/2),
            (self.width/3, self.height/2)]
            
        righttrack = map(tankrot, righttrack)
        
        pygame.draw.polygon(screen, (100, 0, 0), tankpoly, 0)
        
        pygame.draw.polygon(screen, (255, 30, 30), lefttrack, 0)
        pygame.draw.polygon(screen, (255, 30, 30), righttrack, 0)
        
        #pygame.draw.polygon(screen, (255, 0, 0), tankpoly, 2)
        pygame.draw.line(screen, (255, 255, 255), tankpoly[0], tankpoly[1], 2)
        
        pygame.draw.polygon(screen, (255, 0, 0), cannpoly, 0)
        pygame.draw.polygon(screen, (0, 0, 0), cannpoly, 3)
        pygame.draw.line(screen, (255, 255, 255), cannpoly[0], cannpoly[1], 3)
        
        #targeting laser
        pos = rotate((0, -self.cheight/2 - 2), self.pos, self.candir)
        pos2 = rotate((0, -900), pos, self.candir)
        pygame.draw.line(screen, (0, 255, 0), pos, pos2)
        
        
class Birdo:
    speed = 70
    width = 15
    height = 15
    
    def __init__(self, pos):
        self.pos = pos
        self.dir = 0
        
    def move(self):
        self.dir += timescale(.4)
        self.pos = rotate((0, -timescale(self.speed)), self.pos, self.dir)
        
    def draw(self):
        birdpoly = squarefy(self.width, self.height)
        birdoff = lambda x: (self.pos[0] + x[0], self.pos[1] + x[1])
        birdpoly = map(birdoff, birdpoly)
        
        pygame.draw.polygon(screen, (int(random.random()*255), int(random.random()*255), int(random.random()*255)), birdpoly, 0)
        pygame.draw.polygon(screen, (0, 0, 255), birdpoly, 2)
    
class Txt:
    myfont = pygame.font.Font("freesansbold.ttf", 15)

    @classmethod
    def render(cls, string, x, y, alpha = 255):
        # render text
        label = cls.myfont.render(string, 1, (255,255,0))
        #screen.blit(label, (x, y))
        blit_alpha(screen, label, (x, y), alpha)
        
class Alert:
    words = ["BAM!","BANG!","BIFF!","BONK!","CLANK!","CLUNK!","CRACK!","CRASH!","CRUNCH!","KAPOW!","KLONK!","KLUNK!","KRUNCH!","POW!","SOCK!","SPLATS!","SPLAT!","SWISH!","SWOOSH!","THUNK!","THWACK!","THWAP!","WHACK!","WHAM!","WHAP!","ZWAP!","ZAM!","ZAP!","ZOK!"]
    
    def __init__(self, pos, offset, born, ttl, string):
        self.pos = pos
        self.offset = offset
        self.born = born
        self.ttl = ttl
        if string:
            self.string = string
        else:
            self.string = random.choice(self.words)
        
        self.pos = rotate((0, -self.offset), self.pos, random.random()*2*pi)
    def alive(self):
        return pygame.time.get_ticks() < self.born + self.ttl
    def draw(self):
        alpha = 255 - int((pygame.time.get_ticks() - self.born) * 255.0 / 1000)
        Txt.render(self.string, self.pos[0], self.pos[1], alpha)
        
        
t = Tank((width/2, height/2), 0, 0, 100, 1500)
b = Birdo((width/4, height/2))
proj = []
sparks = []
alerts = []

inputs = {
    'left': False,
    'right': False,
    'cleft': False,
    'cright': False,
    'move': False,
    'reverse': False,
    'fire': False,
    'bullets_fired': 0,
    'conkey': False,
    'debug': False,
    'score': 0,
    'rumble': None,
    'motor': None,
    'done': False,
    'last_frame': None
    }
    
def handle_input():
    global inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            inputs['done'] = True
            break
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                inputs['done'] = True
            if event.key == K_BACKQUOTE:
                inputs['conkey'] = True
            if event.key == K_LEFT:
                inputs['cleft'] = True
            if event.key == K_RIGHT:
                inputs['cright'] = True
            if event.key == K_a:
                inputs['left'] = True
            if event.key == K_d:
                inputs['right'] = True
            if event.key == K_w:
                inputs['move'] = True
            if event.key == K_s:
                inputs['reverse'] = True
            if event.key == K_LCTRL:
                inputs['fire'] = True
        if event.type == pygame.KEYUP:
            if event.key == K_BACKQUOTE:
                inputs['conkey'] = False
            if event.key == K_LEFT:
                inputs['cleft'] = False
            if event.key == K_RIGHT:
                inputs['cright'] = False
            if event.key == K_a:
                inputs['left'] = False
            if event.key == K_d:
                inputs['right'] = False
            if event.key == K_w:
                inputs['move'] = False
            if event.key == K_s:
                inputs['reverse'] = False
            if event.key == K_LCTRL:
                inputs['fire'] = False
                
def advance_state():
    global alerts, proj, sparks
    trot = 1
    if inputs['left']:
        t.dir -= timescale(trot)
        t.candir -= timescale(trot)
    if inputs['right']:
        t.dir += timescale(trot)
        t.candir += timescale(trot)
    crot = .75 if not inputs['left'] and not inputs['right'] else .5
    if inputs['cleft']:
        t.candir -= timescale(crot)
    if inputs['cright']:
        t.candir += timescale(crot)
    if inputs['move'] and not inputs['reverse']:
        t.move()
    b.move()
    if inputs['reverse'] and not inputs['move']:
        t.reverse()
    if inputs['fire']:
        if t.fire():
            inputs['bullets_fired'] += 1
            fire = False

    if inputs['conkey']:
        inputs['debug'] = not inputs['debug']
        inputs['conkey'] = False
        
        #sound
    if (inputs['move'] and not inputs['reverse']) \
            or (not inputs['move'] and inputs['reverse']) \
            or (inputs['left'] and not inputs['right']) \
            or (not inputs['left'] and inputs['right']):
        if not inputs['rumble']:
            inputs['rumble'] = sounds['engine'].play(-1)
        try:
            if inputs['move']:
                rumble.set_volume(.4)
            elif inputs['reverse']:
                rumble.set_volume(.3)
            else:
                rumble.set_volume(.25)
        except:
            pass
    else:
        if inputs['rumble']:
            inputs['rumble'].stop()
            inputs['rumble'] = None
            
    if (inputs['cleft'] and not inputs['cright']) \
            or (not inputs['cleft'] and inputs['cright']):
        if not inputs['motor']:
            inputs['motor'] = sounds['whine'].play(-1)
            try:
                inputs['motor'].set_volume(.3)
            except:
                pass
    else:
        if inputs['motor']:
            inputs['motor'].stop()
            inputs['motor'] = None
            
    def onscreen(pos): 
        return pos[0] >= 0 and pos[0] <= width and pos[1] >= 0 and pos[1] <= height
    def collide(p):
        global score
        x, y = p.pos
        xmin = b.pos[0] - b.width/2
        xmax = b.pos[0] + b.width/2
        ymin = b.pos[1] - b.height/2
        ymax = b.pos[1] + b.height/2
        if x <= xmax and x >= xmin and y <= ymax and y >= ymin:
            inputs['score'] += 1
            sounds['beep'].play()
            # alert
            pos = (x, y)
            a = Alert(pos, 3*b.width/2, pygame.time.get_ticks(), 1000, None)
            alerts.append(a)
            return True
        return False
        
    alerts = [a for a in alerts if a.alive()]
    
    for p in proj:
        p.move()
    proj = [p for p in proj if onscreen(p.pos) and not collide(p)]
    
    for s in sparks:
        s.move()
    sparks = [s for s in sparks if s.alive()]
def draw_scene():
    screen.fill((0,0,0))
    
    t.draw()
    b.draw()
    
    [a.draw() for a in alerts]
        
    [p.draw() for p in proj]
    
    [s.draw() for s in sparks]
    

    if inputs['debug']:
        Txt.render("Bullets Fired: "+str(inputs['bullets_fired']), 10, 10)
        Txt.render("Bullets On Screen: "+str(len(proj)), 10, 30)
        Txt.render("t.x: "+str(t.pos[0]), 10, 50)
        Txt.render("t.y: "+str(t.pos[1]), 10, 70)
        
        #fps = 1.0/(int(round(time.time() * 1000))-inputs['last_frame']) if inputs['last_frame'] else 0
        if conn.server:
            Txt.render("NETWORK OPS / SEC: "+str(clock.get_fps()), 10, 90)
            Txt.render("FPS              : "+str(inputs['fps']), 10, 110)
        else:
            Txt.render("FPS              : "+str(clock.get_fps()), 10, 110)
        
        screen.set_at((int(t.pos[0]), int(t.pos[1])), (255,255,255))
    Txt.render("Score: "+str(inputs['score']), 10, height-25)
    
def input_call():
    print "SENDING KEEPALIVE TO SERVER"
    str = "HELLO KEEP ME ALIVE"
    conn.req_echo(str)
    
conn = EchoClient()

def tick_begin():
   #global ms
   #ms = clock.tick_busy_loop(120)
   #print ms
   handle_input()
   
   #send network events
   #reactor.callInThread(conn.req_echo("TEST"))
   d = threads.deferToThread(conn.req_echo, "TEST_DEFERRED_TO_THREAD")
   #d.addCallbacks(tick_return, conn.err)
def tick_return(response):
    #network events have been receiveed
    global seq
    seq = seq + 1
    print "TICK RETURN GOT: " + str(response) + " | " + str(seq)
    
    global ms
    ms = clock.tick()
    
    
    if inputs['done']:
        conn.quit()
    else:
        tick_begin()
        
def local_stuff():
    now = pygame.time.get_ticks()
    global lms
    if inputs['last_frame']:
        lms = now - inputs['last_frame']
    else:
        lms = 0
    if inputs['last_frame']:
        inputs['fps'] = 1000.0/(now-inputs['last_frame'])
    advance_state()
    draw_scene()
    pygame.display.update()
    inputs['last_frame'] = pygame.time.get_ticks()
        
def single_player():
    while not inputs['done']:
        global ms
        ms = clock.tick_busy_loop(240)
        handle_input()
        advance_state()
        draw_scene()
        pygame.display.update()
    conn.quit()
    
if __name__ == "__main__":
    conn = EchoClient()
    conn.connect()
    lc = LoopingCall(local_stuff)
    lc.start(1.0/240)
    reactor.run()
    pygame.quit()
