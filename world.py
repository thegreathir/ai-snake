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

    def __init__(self, x, y, direction, color):
        self.body = [(x, y)]
        self.score = 0
        self.direction = direction
        self.length = 1
        self.growing = False
        self.color = color

    def get_head(self):
        return self.body[-1]


class World:
    COLORS = ["red", "green", "blue", "magneta", "cyan"]
    def __init__(self):
        self.height = 12
        self.width = 40
        self.min_score = 1
        self.max_score = 15
        self.score_c = 5
        self.snake_num = 3

        self.scores = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(random.randint(self.min_score, self.max_score))
            self.scores.append(row)

        self.snakes = []
        for i in range(self.snake_num):
            self.snakes.append(Snake(random.randint(0, self.width-1), random.randint(0, self.height-1), "rlud"[random.randint(0,3)], World.COLORS[i]))

    def move_snake(self, snake , new_direction=None):

        head = snake.get_head()
        if len(snake.body) == 1:
            snake.score += self.score_c * self.scores[head[1]][head[0]] + 1
            snake.length = self.scores[head[1]][head[0]] + 1
            snake.growing = True
        else:
            if len(snake.body) == snake.length:
                snake.growing = False

        direction = snake.direction
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
        snake.body.append(nxt)
        if not snake.growing:
            snake.body.pop(0)
            snake.body.pop(0)

    def start(self, ai):
        cursor.hide()
        os.system("clear")
        while True:
            render(self)
            for snake in self.snakes:
                snake.direction = ai.get_action(snake)
                self.move_snake(snake)
            time.sleep(0.5)
