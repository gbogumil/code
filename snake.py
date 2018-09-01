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
    position = (0,0)
    value = 1

    def __init__(self, x, y, value):
        position = (x,y)

    def update(self, app):
        pass

class Player:
    positions = []
    maxlength = 150

    speed = 5
    direction = 0.0
    turnspeed = dtor * 5.0 # measured in radians
    speedspeed = 0.25
    maxspeed = 32
    minspeed = 3
    app = None

    bounce = True

    def __init__(self, app):
        self.positions.append((10.0,10.0, self.direction))
        self.app = app

    def bounce(self, pos):
        # calculate the position based on the angle the snake is moving
        deltax = self.speed * math.cos(self.direction)
        deltay = self.speed * math.sin(self.direction)
        newx = pos[0] + deltax
        newy = pos[1] + deltay
        newdir = self.direction
        
        # did we hit the top or bottom
        if newy <= 0 or newy >= self.app.windowHeight:
            newy = pos[1] - deltay
            newdir = (2 * math.pi) - self.direction
        # did we hit the right or left
        if newx < 0 or newx >= self.app.windowWidth:
            newx = pos[0] - deltax
            newdir = (2 * math.pi) - ((self.direction + (math.pi / 2) % (2 * math.pi))) - (math.pi / 2)
        #ensure direction stays in 0..2pi
        newdir = newdir % (2 * math.pi)
        fmt = '\n{0:.2f}, {1:.2f} {2:.2f}\n{3:.2f}, {4:.2f} {5:.2f}\n{6:.2f}, {7:.2f}'
        logging.info(fmt.format(pos[0], pos[1], self.direction, newx, newy, newdir, deltax, deltay))
        return newx, newy, newdir

    def update(self, app):
        newx = 0
        newy = 0

        if self.bounce:
            newx, newy, self.direction = self.bounce(self.positions[len(self.positions)-1])
        else:
            pass

        newpos = (newx,newy,self.direction)
        # if we run into ourself then chop off the tail
        # skip the last 5 in the array (which is the head + 4)
        for i in range(0,max(0,len(self.positions)-1-5)):
            boxsize = min(4, self.speed/1.5)
            if self.hit(self.positions[i], newpos,boxsize):
                self.positions = self.positions[i+1::]
                break
        # this lets the positions flow through the array
        if len(self.positions)  >= self.maxlength:
            self.positions.remove(self.positions[0])
        self.positions.append(newpos)

    def moveClock(self):
        self.direction = (self.direction + self.turnspeed) % (2.0 * math.pi)

    def moveCounter(self):
        self.direction = (self.direction - self.turnspeed) % (2.0 * math.pi)

    def speedUp(self):
        self.speed = self.speed + self.speedspeed
        if self.speed > self.maxspeed:
            self.speed = self.maxspeed

    def speedDown(self):
        self.speed = self.speed - self.speedspeed
        if self.speed < self.minspeed:
            self.speed = self.minspeed
    
    def hit(self, pos1, pos2, boxsize):
        return \
            pos1[0] > (pos2[0] - boxsize) and \
            pos1[0] < (pos2[0] + boxsize) and \
            pos1[1] > (pos2[1] - boxsize) and \
            pos1[1] < (pos2[1] + boxsize)

class App:
    windowWidth = 800
    windowHeight = 600
    player = None
    edibles = []

    def on_init(self):
        self.player = Player(self)
        self.edibles.append(Edible(50, 50, 1))
        pygame.init()
        windowSize = (self.windowWidth,self.windowHeight)
        self._display_surf = pygame.display.set_mode(
            (windowSize), pygame.HWSURFACE)
 
        pygame.display.set_caption('Snakey eats shiney edibles')
        self._running = True
        self._image_surf = pygame.image.load("pygame.png")
        self._image_surf.set_colorkey(self._image_surf.get_at((0,0)), RLEACCEL)   
        self._image_surf = self._image_surf.convert()
 
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
 
    def on_loop(self):
        pass
 
    def on_render(self):
        self._display_surf.fill((0,0,0))

        i = 0
        for i in range(0,len(self.player.positions)):
            pos = self.player.positions[i]
            wrappedpos = (pos[0]%self.windowWidth,pos[1]%self.windowHeight)

            rotdeg = -360.0 * pos[2] / math.pi / 2.0

            self._display_surf.blit(
                pygame.transform.rotate(self._image_surf,rotdeg), pos[0:2])
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
        lastkey = None
        while( self._running ):
            pygame.event.pump()
            keys = pygame.key.get_pressed() 
 
            if (keys[K_RIGHT]):
                lastkey = K_RIGHT
            if (keys[K_LEFT]):
                lastkey = K_LEFT
            if (keys[K_UP]):
                lastkey = K_UP
            if (keys[K_DOWN]):
                lastkey = K_DOWN
            if (keys[K_ESCAPE]):
                self._running = False

            if self._running:
                if nextupdate < current_milli():
                    nextupdate = current_milli() + update_freq
                    action = actionmap.get(lastkey, lambda:0)
                    lastkey = None
                    action()
                    self.player.update(self)
                    for e in self.edibles:
                        e.update(self)
                self.on_loop()
                self.on_render()
            
        self.on_cleanup()
 
if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    theApp = App()
    theApp.on_execute()