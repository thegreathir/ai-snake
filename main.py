from world import World
from agent import Agent, RandomAgent
import sys

if __name__ == "__main__":
    world = World("config.json")
    agent1 = Agent(world)
    agent2 = Agent(world)
    simulation_mode = sys.argv.count("-s") == 1
    world.start(simulation_mode)

# todo
# amount
# min max
# turn and agent
# worm body
# growing coloring
