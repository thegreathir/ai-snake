from world import World
from ai import Ai
import sys

if __name__ == "__main__":
    world = World()
    ai = Ai(world)
    simulation_mode = sys.argv.count("-s") == 1
    world.start(ai, simulation_mode)
