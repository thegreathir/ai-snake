from world import World
from agent import Agent
import sys

if __name__ == "__main__":
    world = World("config.json")
    agent = Agent(world)
    simulation_mode = sys.argv.count("-s") == 1
    world.start(simulation_mode)

# todo
# amount
# min max
# turn and agent
# worm body
# growing coloring
