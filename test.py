<<<<<<< HEAD
from pygame.locals import *
import pygame
import logging as log

class maze:
    def __init__(self, board):
        self.board = board
        self.boxSize = 10

class app:
    def __init__(self):
        log.basicConfig(level=log.DEBUG)
        log.info('setting board')
        board = [
            [1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 1],
            [1, 1, 0, 1, 0, 1],
            [1, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1]
        ]
        self.maze = maze(board)
        log.info('init pyg')
        pygame.init()
        log.info('getting font')
        self.debugFont = pygame.font.Font(None, 20)
        
        log.info('init display')
        self.display = pygame.display.set_mode((800,600), pygame.HWSURFACE)
        pygame.display.set_caption('a maze')

        self.running = True

        while (self.running):
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if keys[K_ESCAPE]:
                log.info('hit escape')
                self.running = False
            w = len(self.maze.board[0])
            h = len(self.maze.board)
            #log.info('drawing maze ({0},{1})'.format(w, h))
            for x in range(w):
                for y in range(h):
                    if self.maze.board[y][x]:
                        box = Rect(
                            x * self.maze.boxSize,
                            y * self.maze.boxSize,
                            self.maze.boxSize,
                            self.maze.boxSize
                        )
                        self.display.fill((255,255,0), box)
            pygame.display.flip()
a = app()
=======
import logging as log

class Primes:
    def __init__(self):
        try:
            file = open('primes.bin', 'r')
            self._primes = file.read()
            close(file)
        except:
            self._primes = []
            
    def save(self):
        file = open('primes.bin', 'w')
        file.write(self._primes)
        close(file)
    
    def findPrimes(self, value):


    def isPrime(self, value):
        foundNewPrime=False
        if self._primes[-1]**2 < value:
            for (p in findPrimes(self, value)):
                pass

        for i in range(len(self._primes)):
            if float(value)/self._primes[i] == int(value/self._primes[i]):
                return False
        return true

    def upTo(self, value):
        if (self._primes[-1] <= value):
            for (i in range(len(self._primes))):
                yield self._primes[i]
        else:
            for (p in findPrimes(self, value):
                yield p
>>>>>>> 1994f3e2ff108c68c300463cd51de51047b9bc5e
