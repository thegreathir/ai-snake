from dls import get_dls_action
from world import *
import random


def get_random_action():
    act_int = random.randint(1, 4)
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT][act_int - 1]


class Ai:

    def __init__(self, world):
        self.world = world

    def get_action(self, snake):
        return get_dls_action(self.world, snake)
