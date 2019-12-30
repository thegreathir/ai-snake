from dls import get_dls_action
from gs import get_gs_action
from world import *
import random


def get_random_action():
    act_int = random.randint(1, 4)
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT][act_int - 1]


class Agent:

    def __init__(self, world):
        self.snake_id = world.register(self)

    def get_action(self, world):
        return get_dls_action(world, world.snakes[self.snake_id])
        # return get_gs_action(self.world, snake)
