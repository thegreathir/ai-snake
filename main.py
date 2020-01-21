import json
import sys
from world import World, Side
from agent import AlphaBetaAgent, RandomAgent, HumanAgent


def get_agent(name, properties):
    if name == "random":
        return RandomAgent(world)
    if name == "alphabeta":
        return AlphaBetaAgent(world, properties)
    if name == "human":
        return HumanAgent(world)


if __name__ == "__main__":
    with open("config.json", 'r') as config_file:
        json_config = json.loads(config_file.read())

    if not json_config:
        sys.exit(1)

    world = World(json_config)
    agents = []

    for i in range(json_config["players_per_team"] * 2):
        if i % 2 == Side.A:
            agents.append(get_agent(json_config["agent_a"]["type"], json_config["agent_a"]["properties"]))
        elif i % 2 == Side.B:
            agents.append(get_agent(json_config["agent_b"]["type"], json_config["agent_b"]["properties"]))

    world.start()
