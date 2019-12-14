from world import *
import random

class Ai:

    def __init__(self, world):
        self.world = world

    def get_action(self, snake):
        act_int = random.randint(1,4)
        return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT][act_int - 1]
