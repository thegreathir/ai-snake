from ai.dls import get_dls_action
from ai.gs import get_gs_action
from world import *
import random
from ai import cppagent

def get_random_action():
    act_int = random.randint(1, 4)
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT][act_int - 1]


class Agent:

    def __init__(self, world):
        self.snake_id = world.register(self)

    def get_action(self, world):
        return cppagent.get_alphabeta_action(world.to_json(self.snake_id), 16)

class RandomAgent:

    def __init__(self, world):
        world.register(self)

    def get_action(self, world):
        return get_random_action()
