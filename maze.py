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