import random
import logging

rand = random.random
logging.basicConfig(level=logging.INFO)

class Player:

    def __init__(self, v):
        self.positions = []
        self.positions.append(v)
    
    def toString(self):
        return 'v = {0}'.format(self.positions[0])


p1 = Player(1)
p2 = Player(2)

logging.info(p1.toString())
logging.info(p2.toString())