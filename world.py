import random
import time
import cursor
import os

from ui import render


class Direction:
    RIGHT = "r"
    LEFT = "l"
    UP = "u"
    DOWN = "d"


class Snake:

    def __init__(self, x, y, direction):
        self.body = [(x, y)]
        self.score = 0
        self.direction = direction
        self.length = 1
        self.growing = False

    def get_head(self):
        return self.body[-1]


class World:
    def __init__(self):
        self.height = 12
        self.width = 40
        self.min_score = 1
        self.max_score = 15

        self.scores = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(random.randint(self.min_score, self.max_score))
            self.scores.append(row)

        self.snake = Snake(0, 0, Direction.RIGHT)

    def move_snake(self, new_direction=None):

        head = self.snake.get_head()
        if len(self.snake.body) == 1:
            self.snake.score += self.scores[head[1]][head[0]]
            self.snake.length = self.scores[head[1]][head[0]] + 1
            self.snake.growing = True
        else:
            if len(self.snake.body) == self.snake.length:
                self.snake.growing = False

        direction = self.snake.direction
        if new_direction:
            direction = new_direction

        nxt = None
        if direction == Direction.RIGHT:
            nxt = (head[0] + 1, head[1])
        elif direction == Direction.LEFT:
            nxt = (head[0] - 1, head[1])
        elif direction == Direction.UP:
            nxt = (head[0], head[1] - 1)
        elif direction == Direction.DOWN:
            nxt = (head[0], head[1] + 1)
        self.snake.body.append(nxt)
        if not self.snake.growing:
            self.snake.body.pop(0)
            self.snake.body.pop(0)

    def start(self, ai):
        cursor.hide()
        os.system("clear")
        print()
        while True:
            render(self)
            self.snake.direction = ai.get_action()
            self.move_snake()
            time.sleep(0.5)
