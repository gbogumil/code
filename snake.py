from pygame.locals import *
import pygame
import time
import math
import logging
import random

rand = random.random

deg_to_rad = math.pi * 2.0 / 360.0
twopi = 2.0 * math.pi
halfpi = math.pi / 2.0

max = lambda x,y: x if x > y else y
min = lambda x,y: x if x < y else y
current_milli = lambda: int(round(time.time() * 1000))

class Edible:
    def __init__(self, x, y, value):
        self.position = [x,y]
        self.value = value

    def update(self, app):
        pass


class Player:
    instanceCounter = 0
    maxlength = 250
    minlength = 5

    turnspeed = deg_to_rad * 6.0 # measured in radians
    speedspeed = 0.4
    maxspeed = 10
    minspeed = 3

    def __init__(self, x, y):
        self.identifier = self.instanceCounter
        self.instanceCounter += 1
        self.positions = []
        self.speed = self.minspeed
        self.cooldown = 10
        self.direction = (2.0 * math.pi) * rand()
        for i in range(0, 5):
            self.positions.append((x, y, self.direction))
        self.nextPos = self.positions[-1]
        self.nextSpeed = self.speed
        self.nextDir = self.direction
        self.moveGenerator = self.randomGenerator()
        self.speedGenerator = self.randomGenerator()
        logging.info('created player {0:.3f} {1:.2f},{2:.2f} {3:.2f}'.format(
            self.direction, self.positions[-1][0], self.positions[-1][1], self.speed
        ))
        self.storedGrowth = 0

    def update(self, app):
        # determine the desired next position * direction
        if not self.positions:
            return
        curpos = self.positions[-1]
        newx = curpos[0] + (self.nextSpeed * math.cos(self.nextDir))
        newy = curpos[1] + (self.nextSpeed * math.sin(self.nextDir))
        self.nextPos = (newx,newy)

    def moveClock(self):
        #logging.info('move clockwise {0}'.format(self.direction))
        self.nextDir = (self.direction + self.turnspeed) % (2.0 * math.pi)

    def moveCounter(self):
        #logging.info('move counter-clockwise {0}'.format(self.direction))
        self.nextDir = (self.direction - self.turnspeed) % (2.0 * math.pi)

    def speedUp(self):
        #logging.info('speed up {0}'.format(self.speed))
        self.nextSpeed = self.speed + self.speedspeed
        if self.nextSpeed > self.maxspeed:
            self.nextSpeed = self.maxspeed

    def speedDown(self):
        #logging.info('speed down {0}'.format(self.speed))
        self.nextSpeed = self.speed - self.speedspeed
        if self.nextSpeed < self.minspeed:
            self.nextSpeed = self.minspeed

    def grow(self, value):
        self.storedGrowth += value
    
    def randomGenerator(self):
        while True:
            ret = rand() * 3.0
            randcooldown = int(rand() * (self.cooldown+1))
            for i in range(0,randcooldown):
                yield ret

    def indicateIntent(self):
        move = next(self.moveGenerator)
        if move < 1.0:
            self.moveClock()
        elif move < 2.0:
            pass
        else:
            self.moveCounter()

        speed = next(self.speedGenerator)
        if speed < 1.0:
            self.speedUp()
        elif speed < 2.0:
            pass
        else:
            self.speedDown()

    def toString(self):
        # speed direction cooldown positions position[-1]
        fmt = '{0} {1:.2f} {2} {3} {4:.2f} {5:.2f}'
        return fmt.format(
            self.speed, 
            self.direction, 
            self.cooldown, 
            len(self.positions),
            self.positions[-1][0], 
            self.positions[-1][1]
        )

class App:
    # conversion to viewport of main player within largerworld
        # need a viewport size
        # game dimension need to be determined either 
            # finite bounded
                # with death at edge
                # with bounce
            # finite unbounded

    def __init__(self):
        self.hitBox = None
        self.drones = []
        self.drawDebug = True
        self.viewportWidth = 800
        self.viewportHeight = 600
        self.worldWidth = self.viewportWidth * 4
        self.worldHeight = self.viewportHeight * 4
        self.border = 100
        self.player = None
        self.drones = []
        self.droneCount = 4
        self.edibles = []
        self._images = {}
        self.playerGenerator = None
        self.ediblesGenerator = None
        self.debugFont = None

    def randomPosition(self):
        return (
                rand() * (self.worldWidth - (2 * self.border)) + self.border,
                rand() * (self.worldHeight - (2 * self.border)) + self.border
        )

    def createPlayer(self):
        while True:
            initialpos = self.randomPosition()
            yield Player(initialpos[0], initialpos[1])

    def createEdible(self):
        while True:
            initialpos = self.randomPosition()
            v = int(rand() * 10)
            yield Edible(initialpos[0], initialpos[1], v)

    def playerBounce(self, player):
        # calculate the position based on the angle the snake is moving
        deltax = player.speed * math.cos(player.direction)
        deltay = player.speed * math.sin(player.direction)
        pos = player.positions[len(player.positions)-1]
        newx = pos[0] + deltax
        newy = pos[1] + deltay
        newdir = player.direction
        
        # did we hit the top or bottom
        if newy <= 0 or newy >= self.worldHeight:
            newy = pos[1] - deltay
            newdir = (2 * math.pi) - player.direction
        # did we hit the right or left
        if newx < 0 or newx >= self.worldWidth:
            newx = pos[0] - deltax
            newdir = (2 * math.pi) - ((player.direction + (math.pi / 2) % (2 * math.pi))) - (math.pi / 2)
        #ensure direction stays in 0..2pi
        newdir = newdir % (2 * math.pi)
        return newx, newy, newdir

    def playerWrap(self, player):
        pos = player.nextPos
        player.direction = player.nextDir
        pos = (pos[0] % self.worldWidth, pos[1] % self.worldHeight, player.direction)
        player.positions.append(pos)
        if player.storedGrowth == 0:
            player.positions.remove(player.positions[0])
        else:
            player.storedGrowth -= 1
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

    def collisionActions(self, player):
        #here we determine
        # 1. if the player tail needs to be cut and converted to edibles
        box = self._images['player'].get_rect()
        box.left = player.positions[-1][0]
        box.top = player.positions[-1][1]
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
        logging.info('chopping p{1} at {0}'.format(i, player.identifier))
        newEdibles = player.positions[:i]
        player.positions = player.positions[i+1:]
        for p in newEdibles:
            self.edibles.append(Edible(p[0], p[1], 1))

    def growPlayer(self, player, edible):
        player.grow(edible.value)
        self.edibles.remove(edible)
        #self.edibles.append(next(self.ediblesGenerator()))
        if len(player.positions) > player.maxlength:
            chop = len(player.positions) - player.maxlength
            for i in range(0,chop):
                p = player.positions[i]
                self.edibles.append(Edible(p[0], p[1]), 1)
            player.positions = player.positions[:-player.maxlength]

    def hit(self, pos, box):
        return \
            pos[0] > box.left and \
            pos[0] < box.right and \
            pos[1] > box.top and \
            pos[1] < box.bottom

    def drawPlayer(self, player, imageName, drawableArea):
        for i in range(0,len(player.positions)):
            pos = player.positions[i]
            newpos = (
                pos[0] - drawableArea[0],
                pos[1] - drawableArea[1]
            )

            rotdeg = -360.0 * pos[2] / math.pi / 2.0
            self._display_surf.blit(
                pygame.transform.rotate(self._images[imageName],rotdeg), newpos)

    def safePos(self, pos):
        return '({0:.2f}, {1:.2f}, {2:.2f})'.format(pos[0], pos[1], pos[2])

    def on_init(self):
        pygame.init()
        self.debugFont = pygame.font.Font(None, 20)

        playerGenerator = self.createPlayer()
        self.player = next(playerGenerator)
        for droneindex in range(0,self.droneCount):
            drone = next(playerGenerator)
            drone.cooldown = (1+droneindex) * 10
            logging.info('cooldown set to {0}'.format(drone.cooldown))
            self.drones.append(drone)

        self.ediblesGenerator = self.createEdible()
        initialEdibles = (next(self.ediblesGenerator) for i in range(0,150))
        for e in initialEdibles:
            self.edibles.append(e)

        windowSize = (self.viewportWidth,self.viewportHeight)
        self._display_surf = pygame.display.set_mode(
            (windowSize), pygame.HWSURFACE)
 
        pygame.display.set_caption('Snakey eats shiney edibles')
        self._running = True
        self._paused = False
        i = self.loadimage('snake.png', True)
        self._images['drone'] = pygame.transform.scale(i, (int(i.get_rect().width/2), int(i.get_rect().height/2)))
        self._images['player'] = self.colorize(self._images['drone'])
        self._images['edible'] = self.loadimage('edible.png', True)

        logging.info('players created')
        logging.info('player = {0}'.format(self.player.toString()))
        for index in range(0, len(self.drones)):
            logging.info('drone {0} = {1}'.format(index, self.drones[index].toString()))
    def loadimage(self, filelocation, transparent):
        ret = pygame.image.load(filelocation)
        if transparent:
            ret.set_colorkey(ret.get_at((0,0)), RLEACCEL)
        return ret.convert()
    
    def colorize(self, image):
        image = image.copy()
        rect = image.get_rect()
        image.lock()
        for x in range(0,rect.width):
            for y in range(0, rect.height):
                oc = image.get_at((x, y))
                newColor = Color(oc.b, oc.g,0, oc.a)
                image.set_at((x, y), newColor)

        image.unlock()
        return image

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
 
    def on_loop(self):
        pass
 
    def on_render_edibles(self, drawableArea):
        for e in self.edibles:
            maxEdibleValue = 10.0
            maxColorValue = 255
            minColorLevel = 2
            circleWidth = 2
            colorComponent = max(e.value, minColorLevel) / maxEdibleValue * maxColorValue
            colorComponent = int(colorComponent % maxColorValue)
            radius = int(colorComponent * maxEdibleValue / maxColorValue)
            c = Color(colorComponent, 0, colorComponent, 0)
            p = (
                int(e.position[0] - drawableArea[0]), 
                int(e.position[1] - drawableArea[1])
            )
            pygame.draw.circle(self._display_surf, c, p, radius, circleWidth)

    def on_render_drones(self, drawableArea):
        for d in self.drones:
            self.drawPlayer(d, 'drone', drawableArea)

    def on_render_player(self, drawableArea):
        self.drawPlayer(self.player, 'player', drawableArea)

    def on_render_debug(self, drawableArea, extras = None):
        if self.drawDebug:
            if self.hitBox:
                newbox = Rect(
                    self.hitBox.left - drawableArea[0], 
                    self.hitBox.top - drawableArea[1],
                    self.hitBox.width,
                    self.hitBox.height)
                self._display_surf.fill((255,255,0), newbox)
            
            if extras:
                offset = 0
                for extra in extras:
                    text = '{0}'.format(extra)
                    s = self.debugFont.render(text, False, Color(255,255,255))
                    self._display_surf.blit(s, (0, offset))
                    offset += self.debugFont.size(text)[1] + 10

    def on_render(self):
        # center viewport as closely as possible to player
        # only render items within the viewport
        drawableArea = [
            self.player.positions[-1][0] - (self.viewportWidth / 2),
            self.player.positions[-1][1] - (self.viewportHeight / 2)
        ]
        if drawableArea[0] < 0:
            drawableArea[0] = 0
        elif drawableArea[0] > self.worldWidth - self.viewportWidth:
            drawableArea[0] = self.worldWidth - self.viewportWidth
        if drawableArea[1] < 0:
            drawableArea[1] = 0
        elif drawableArea[1] > self.worldHeight - self.viewportHeight:
            drawableArea[1] = self.worldHeight - self.viewportHeight
        
        self._display_surf.fill((0,0,0))

        self.on_render_edibles(drawableArea)
        self.on_render_drones(drawableArea)
        self.on_render_player(drawableArea)

        extras = [self.safePos(self.player.positions[-1])]
        for d in self.drones:
            extras.append(self.safePos(d.positions[-1]))

        self.on_render_debug(drawableArea, extras)
        
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
            if (keys[K_d]):
                self.drawDebug = not self.drawDebug

            if self._running:
                if not self._paused and nextupdate < current_milli():
                    # The basic loop will calculate intent of each player
                    # then based on the intent determine if the environment
                    # should affect that intent
                    # then update the items in the environment
                    nextupdate = current_milli() + update_freq
                    for k in keyspressed:
                        actionmap.get(k, lambda:0)()
                    keyspressed = set()

                    for d in self.drones:
                        d.indicateIntent()

                    self.playerWrap(self.player)
                    #self.playerDieAtEdge(self.player)
                    for d in self.drones:
                    #    self.playerDieAtEdge(d)
                        self.playerWrap(d)
                    
                    self.player.update(self)
                    for d in self.drones:
                        d.update(self)

                    for e in self.edibles:
                        e.update(self)

                    for a in self.collisionActions(self.player):
                        a()
                    for d in self.drones:
                        for a in self.collisionActions(d):
                            a()

                    self.on_loop()
                    self.on_render()
            
        self.on_cleanup()
 
if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    theApp = App()
    theApp.on_execute()