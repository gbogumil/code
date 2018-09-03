from pygame.locals import *
import pygame
import time
import math
import logging
import random

rand = random.random

deg_to_rad = math.pi * 2.0 / 360.0

max = lambda x,y: x if x > y else y
min = lambda x,y: x if x < y else y
current_milli = lambda: int(round(time.time() * 1000))

class Edible:
    position = [0,0]
    value = 1

    def __init__(self, x, y, value):
        self.position = [x,y]

    def update(self, app):
        pass


class Player:
    positions = []
    maxlength = 150
    minlength = 5
    nextPos = None
    nextSpeed = None
    nextDir = None

    speed = 5
    direction = 0.0
    turnspeed = deg_to_rad * 5.0 # measured in radians
    speedspeed = 0.25
    maxspeed = 32
    minspeed = 3

    def __init__(self, x, y):
        self.direction = (2.0 * math.pi) * rand()
        for i in range(0, 5):
            self.positions.append((x, y, self.direction))
        self.nextPos = self.positions[-1]
        self.nextSpeed = self.speed
        self.nextDir = self.direction

    def update(self, app):
        # determine the desired next position * direction
        curpos = self.positions[-1]
        newx = curpos[0] + (self.nextSpeed * math.cos(self.nextDir))
        newy = curpos[1] + (self.nextSpeed * math.sin(self.nextDir))
        self.nextPos = (newx,newy)

    def moveClock(self):
        logging.info('move clockwise {0}'.format(self.direction))
        self.nextDir = (self.direction + self.turnspeed) % (2.0 * math.pi)

    def moveCounter(self):
        logging.info('move counter-clockwise {0}'.format(self.direction))
        self.nextDir = (self.direction - self.turnspeed) % (2.0 * math.pi)

    def speedUp(self):
        logging.info('speed up {0}'.format(self.speed))
        self.nextSpeed = self.speed + self.speedspeed
        if self.nextSpeed > self.maxspeed:
            self.nextSpeed = self.maxspeed

    def speedDown(self):
        logging.info('speed down {0}'.format(self.speed))
        self.nextSpeed = self.speed - self.speedspeed
        if self.nextSpeed < self.minspeed:
            self.nextSpeed = self.minspeed

    def grow(self, value):
        for i in range(0,value):
            self.positions.insert(0,self.positions[0])
    

class App:
    drawDebug = False
    windowWidth = 800
    windowHeight = 600
    player = None
    edibles = []
    _images = {}
    hitBox = None

    def createPlayer(self):
        border = 100
        initialpos = (
            rand() * (self.windowWidth - (2 * border)) + border,
            rand() * (self.windowHeight - (2 * border)) + border
        )
        logging.info('starting at {0}'.format(initialpos))
        return Player(initialpos[0], initialpos[1])

    def createEdibles(self):
        while True:
            epos = (
                rand() * self.windowWidth,
                rand() * self.windowHeight
            )
            v = rand() * 100
            yield Edible(epos[0], epos[1], v)

    def playerBounce(self, player):
        # calculate the position based on the angle the snake is moving
        deltax = player.speed * math.cos(player.direction)
        deltay = player.speed * math.sin(player.direction)
        pos = player.positions[len(player.positions)-1]
        newx = pos[0] + deltax
        newy = pos[1] + deltay
        newdir = player.direction
        
        # did we hit the top or bottom
        if newy <= 0 or newy >= self.windowHeight:
            newy = pos[1] - deltay
            newdir = (2 * math.pi) - player.direction
        # did we hit the right or left
        if newx < 0 or newx >= self.windowWidth:
            newx = pos[0] - deltax
            newdir = (2 * math.pi) - ((player.direction + (math.pi / 2) % (2 * math.pi))) - (math.pi / 2)
        #ensure direction stays in 0..2pi
        newdir = newdir % (2 * math.pi)
        #fmt = '\n{0:.2f}, {1:.2f} {2:.2f}\n{3:.2f}, {4:.2f} {5:.2f}\n{6:.2f}, {7:.2f}'
        #logging.info(fmt.format(pos[0], pos[1], self.direction, newx, newy, newdir, deltax, deltay))
        return newx, newy, newdir

    def playerWrap(self, player):
        pos = player.nextPos
        player.direction = player.nextDir
        pos = (pos[0] % self.windowWidth, pos[1] % self.windowHeight, player.direction)
        player.positions.append(pos)
        player.positions.remove(player.positions[0])
        player.speed = player.nextSpeed

    def playerUpdate(self, player):
        # this lets the positions flow through the array
        if len(player.positions) >= player.maxlength:
            self.chopPlayer(player, len(player.positions) - player.maxlength)
        player.positions.append(newpos)
        if len(player.positions) > player.minlength:
            player.positions.remove(1)
        player.direction = player.newDir
        player.speed = player.newSpeed

    def collisionActions(self):
        #here we determine
        player = self.player
        # 1. if the player tail needs to be cut and converted to edibles
        box = self._images['snake'].get_rect()
        box.left = self.player.positions[-1][0]
        box.top = self.player.positions[-1][1]
        self.hitBox = box
        for i in range(0,max(0,len(player.positions)-1-10)):
            # if we run into ourself then chop off the tail
            # skip the last 5 in the array (which is the head + 4)
            if self.hit(player.positions[i], box):
                yield lambda: self.chopPlayer(player, i)
                break
        # 2. if the player ate an edible
        # this needs to be converted into a hashed list so the positions
        # can be searched more efficiently
        eatenEdibles = []
        for e in self.edibles:
            if self.hit(e.position, box):
                yield lambda: self.growPlayer(player, e)

        # 3> eventually if any players died by running into each other

    def chopPlayer(self, player, i):
        newEdibles = player.positions[:i]
        self.player.positions = self.player.positions[i+1:]
        for p in newEdibles:
            self.edibles.append(Edible(p[0], p[1], 1))

    def growPlayer(self, player, edible):
        player.grow(edible.value)
        self.edibles.remove(edible)
        self.edibles.append(next(self.createEdibles()))

    def hit(self, pos, box):
        return \
            pos[0] > box.left and \
            pos[0] < box.right and \
            pos[1] > box.top and \
            pos[1] < box.bottom

    def on_init(self):
        pygame.init()

        self.player = self.createPlayer()
        initialEdibles = (next(self.createEdibles()) for i in range(0,50))
        for e in initialEdibles:
            self.edibles.append(e)

        windowSize = (self.windowWidth,self.windowHeight)
        self._display_surf = pygame.display.set_mode(
            (windowSize), pygame.HWSURFACE)
 
        pygame.display.set_caption('Snakey eats shiney edibles')
        self._running = True
        self._paused = False
        self._images['snake'] = self.loadimage('snake.png', True)
        self._images['edible'] = self.loadimage('edible.png', True)

    def loadimage(self, filelocation, transparent):
        ret = pygame.image.load(filelocation)
        if transparent:
            ret.set_colorkey(ret.get_at((0,0)), RLEACCEL)
        return ret.convert()
    
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
 
    def on_loop(self):
        pass
 
    def on_render(self):
        self._display_surf.fill((0,0,0))

        for e in self.edibles:
            self._display_surf.blit(
                self._images['edible'], e.position[0:2]
            )

        for i in range(0,len(self.player.positions)):
            pos = self.player.positions[i]

            rotdeg = -360.0 * pos[2] / math.pi / 2.0

            self._display_surf.blit(
                pygame.transform.rotate(self._images['snake'],rotdeg), pos[0:2])

        if self.drawDebug:
            if self.hitBox:
                self._display_surf.fill((255,255,0), self.hitBox)
        pygame.display.flip()
 
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        actionmap = {
            K_RIGHT: self.player.moveClock,
            K_LEFT: self.player.moveCounter,
            K_UP: self.player.speedUp,
            K_DOWN: self.player.speedDown
        }

        update_freq = 1000 / 30 # 30 times per second
        nextupdate = current_milli() + update_freq
        keyspressed = set()
        while( self._running ):
            # user inputs move suggestion
            # players desired next position is determined
            # players desired next direction is determined
            # environment determines where each new position will be
            # environment updates players (position, state)
            # environment updates players 
            pygame.event.pump()
            keys = pygame.key.get_pressed() 
 
            if (keys[K_RIGHT]):
                keyspressed.add(K_RIGHT)
            if (keys[K_LEFT]):
                keyspressed.add(K_LEFT)
            if (keys[K_UP]):
                keyspressed.add(K_UP)
            if (keys[K_DOWN]):
                keyspressed.add(K_DOWN)
            if (keys[K_ESCAPE]):
                self._running = False
            if (keys[K_PAUSE]):
                self._paused = not self._paused

            if self._running:
                if not self._paused and nextupdate < current_milli():
                    nextupdate = current_milli() + update_freq
                    for k in keyspressed:
                        actionmap.get(k, lambda:0)()
                    keyspressed = set()
                    self.playerWrap(self.player)
                    self.player.update(self)
                    for e in self.edibles:
                        e.update(self)
                    for a in self.collisionActions():
                        a()
                self.on_loop()
                self.on_render()
            
        self.on_cleanup()
 
if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    theApp = App()
    theApp.on_execute()