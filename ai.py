from world import *

class Ai:

    def __init__(self, world):
        self.world = world

    def is_head_out(self, head):
        i = head[0]
        j = head[1]
        return (i == -1 or
                i == self.world.width or
                j == -1 or
                j == self.world.height)

    def get_action(self):
        res = ""
        snake_dir = self.world.snake.direction
        while True:
            head = self.world.snake.body[-1]

            if snake_dir == Direction.LEFT:
                head = (head[0] - 1, head[1])
                res = Direction.LEFT
                snake_dir = Direction.UP
            elif snake_dir == Direction.UP:
                head = (head[0], head[1] - 1)
                res = Direction.UP
                snake_dir = Direction.RIGHT
            elif snake_dir == Direction.RIGHT:
                head = (head[0] + 1, head[1])
                res = Direction.RIGHT
                snake_dir = Direction.DOWN
            elif snake_dir == Direction.DOWN:
                head = (head[0], head[1] + 1)
                res = Direction.DOWN
                snake_dir = Direction.LEFT

            if not self.is_head_out(head):
                break
        return res

