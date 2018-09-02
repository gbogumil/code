from pygame.locals import *
import pygame
import time
import math
import logging
import random

rand = random.random

dtor = math.pi * 2.0 / 360.0

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
    nextPos = None
    nextSpeed = None
    nextDir = None

    speed = 5
    direction = 0.0
    turnspeed = dtor * 5.0 # measured in radians
    speedspeed = 0.25
    maxspeed = 32
    minspeed = 3

    def __init__(self, x, y):
        self.direction = (2.0 * math.pi) * rand()
        self.positions.append((x, y, self.direction))


    def update(self, app):
        # determine the desired next position * direction
        curpos = self.positions[len(self.positions) - 1]
        newx = curpos[0] + (self.nextSpeed * math.cos(self.nextDir))
        newy = curpos[1] + (self.nextSpeed * math.sin(self.nextDir))

        self.nextPos = (newx,newy)

    def moveClock(self):
        self.nextDir = (self.direction + self.turnspeed) % (2.0 * math.pi)

    def moveCounter(self):
        self.nextDir = (self.direction - self.turnspeed) % (2.0 * math.pi)

    def speedUp(self):
        self.nextSpeed = self.speed + self.speedspeed
        if self.nextSpeed > self.maxspeed:
            self.nextSpeed = self.maxspeed

    def speedDown(self):
        self.nextSpeed = self.speed - self.speedspeed
        if self.nextSpeed < self.minspeed:
            self.nextSpeed = self.minspeed
    

class App:
    windowWidth = 800
    windowHeight = 600
    player = None
    edibles = []
    _images = {}

    def createPlayer(self):
        border = 100
        initialpos = (
            rand() * self.windowWidth - (2 * border) + border,
            rand() * self.windowHeight - (2 * border) + border
        )
        logging.info('starting at {0}'.format(initialpos))
        return Player(initialpos)

    def createEdibles(self):
        for i in range(50):
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
        pos = player.positions[len(player.positions) - 1]
        return pos[0] % self.windowWidth, pos[1] % self.windowHeight, player.direction

    def playerUpdate(self, player):
        # this lets the positions flow through the array
        if len(player.positions)  >= playerself.maxlength:
            player.positions.remove(player.positions[0])
        player.positions.append(newpos)

    def collisionActions(self):
        #here we determine
        player = self.player
        # 1. if the player tail needs to be cut and converted to edibles
        boxsize = min(16, player.speed/1.5)
        for i in range(0,max(0,len(player.positions)-1-5)):
            # if we run into ourself then chop off the tail
            # skip the last 5 in the array (which is the head + 4)
            if self.hit(player.positions[i], player.nextPos, boxsize):
                player.positions, choppedpos = player.positions[i+1::], player.positions[:i]
                break
        # 2. if the player ate an edible
        # this needs to be converted into a hashed list so the positions
        # can be searched more efficiently
        for i in range(0, len(self.edibles)):
            if self.hit(player.positions[-1], self.edibles[i].position, boxsize):
                player.grow(self.edibles[i].value)
                self.edibles.remove(self.edibles[i])

        # 3> eventually if any players died by running into each other


    def hit(self, pos1, pos2, boxsize):
        return \
            pos1[0] > (pos2[0] - boxsize) and \
            pos1[0] < (pos2[0] + boxsize) and \
            pos1[1] > (pos2[1] - boxsize) and \
            pos1[1] < (pos2[1] + boxsize)

    def on_init(self):
        pygame.init()

        self.player = self.createPlayer()
        self.edibles = list(self.createEdibles())

        windowSize = (self.windowWidth,self.windowHeight)
        self._display_surf = pygame.display.set_mode(
            (windowSize), pygame.HWSURFACE)
 
        pygame.display.set_caption('Snakey eats shiney edibles')
        self._running = True
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

            if self._running:
                if nextupdate < current_milli():
                    nextupdate = current_milli() + update_freq
                    for k in keyspressed:
                        actionmap.get(k, lambda:0)()
                    keyspressed = set()
                    self.player.update(self)
                    self.playerWrap(self.player)
                    for e in self.edibles:
                        e.update(self)
                    for a in self.collisionActions() a()
                self.on_loop()
                self.on_render()
            
        self.on_cleanup()
 
if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    theApp = App()
    theApp.on_execute()