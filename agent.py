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


class AlphaBetaAgent(Agent):

    def __init__(self, world, properties):
        super().__init__(world)
        self.depth = properties["depth"]

    def get_action(self, world):
        return cppagent.get_alphabeta_action(world.to_json(self.snake_id), self.depth)


class RandomAgent(Agent):

    def get_action(self, world):
        return get_random_action()
