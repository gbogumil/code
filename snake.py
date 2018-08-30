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

class Edible:
    position = (0,0)

    def __init__(self, x, y):
        position = (x,y)

class Player:
    positions = []
    maxlength = 150

    speed = 5
    direction = 0.0
    turnspeed = dtor * 5.0 # measured in radians
    speedspeed = 0.25
    maxspeed = 32
    minspeed = 3

    def __init__(self):
        self.positions.append((10.0,10.0, self.direction))

    def update(self, app):
        pos = self.positions[len(self.positions)-1]
        # calculate the position based on the angle the snake is moving
        deltax = self.speed * math.cos(self.direction)
        deltay = self.speed * math.sin(self.direction)

        if pos[0] + deltax > app.windowWidth or pos[0] + deltax < 0:
            newx = pos[0] - deltax
            newdir = math.acos(-1.0 * math.cos(self.direction))
            #if self.direction > math.pi:
            #    newdir = newdir + math.pi
            logging.info('width -> dir {0} newdir {1}'.format(self.direction, newdir))
            self.direction = newdir
        else:
            newx = pos[0] + deltax
        
        self.direction = self.direction % (2.0 * math.pi)        

        if pos[1] + deltay > app.windowHeight or pos[1] + deltay < 0:
            newy = pos[1] - deltay
            newdir = math.asin(-1.0 * math.sin(self.direction))
            #if self.direction > math.pi:
            #    newdir = newdir + math.pi
            logging.info('height -> dir {0} newdir {1}'.format(self.direction, newdir))
            self.direction = newdir
        else:
            newy = pos[1] + deltay

        self.direction = self.direction % (2.0 * math.pi)  

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
    player = Player()

    def on_init(self):
        pygame.init()
        windowSize = (self.windowWidth,self.windowHeight)
        self._display_surf = pygame.display.set_mode(
            (windowSize), pygame.HWSURFACE)
 
        pygame.display.set_caption('Pygame pythonspot.com example')
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
 
        while( self._running ):
            pygame.event.pump()
            keys = pygame.key.get_pressed() 
 
            if (keys[K_RIGHT]):
                self.player.moveClock()
 
            if (keys[K_LEFT]):
                self.player.moveCounter()
 
            if (keys[K_UP]):
                self.player.speedUp()
 
            if (keys[K_DOWN]):
                self.player.speedDown()
 
            if (keys[K_ESCAPE]):
                self._running = False

            if self._running:
                self.player.update(self)
                self.on_loop()
                self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    theApp = App()
    theApp.on_execute()