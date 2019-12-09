from world import World
from ai import  Ai

if __name__ == "__main__":
    world = World()
    ai = Ai(world)
    world.start(ai)
