from ai.dls import get_dls_action
from ai.gs import get_gs_action
from world import *
import random
import sys, os, termios
from ai import cppagent


def get_random_action():
    act_int = random.randint(1, 4)
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT][act_int - 1]


class Agent:

    def __init__(self, world):
        self.snake_id = world.register(self)


class AlphaBetaAgent(Agent):

    def __init__(self, world, properties):
        super().__init__(world)
        self.depth = properties["depth"]

    def get_action(self, world):
        return cppagent.get_alphabeta_action(world.to_json(self.snake_id), self.depth)


class RandomAgent(Agent):

    def get_action(self, world):
        return get_random_action()


class HumanAgent(Agent):

    @staticmethod
    def getkey():
        TERMIOS = termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
        new[6][TERMIOS.VMIN] = 1
        new[6][TERMIOS.VTIME] = 0
        termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
        c = os.read(fd, 1)
        return c

    def get_action(self, world):
        while True:
            key =  HumanAgent.getkey().decode('utf-8')
            if key == 'w':
                return Direction.UP
            elif key == 's':
                return Direction.DOWN
            elif key == 'a':
                return Direction.LEFT
            elif key == 'd':
                return Direction.RIGHT
