import json
import sys
from world import World, Side
from agent import AlphaBetaAgent, RandomAgent

if __name__ == "__main__":
    json_config = None
    with open("config.json", 'r') as config_file:
        json_config = json.loads(config_file.read())

    if not json_config:
        sys.exit(1)

    world = World(json_config)
    agents = []

    for i in range(json_config["players_per_team"] * 2):
        if i % 2 == Side.A:
            if json_config["agent_a"] == "random":
                agents.append(RandomAgent(world))
        elif i % 2 == Side.B:
            if json_config["agent_b"] == "random":
                agents.append(RandomAgent(world))

    world.start()
