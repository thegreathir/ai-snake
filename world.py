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

    def __init__(self, snake_id, x, y, direction, color):
        self.body = [(x, y)]
        self.score = 0
        self.direction = direction
        self.length = 1
        self.growing = False
        self.color = color
        self.snake_id = snake_id

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
        self.snake_num = 1
        self.cycles = 1000
        self.cycle = 0

        self.scores = []
        self.table = {}

        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(random.randint(self.min_score, self.max_score))
            self.scores.append(row)

        self.snakes = []
        for i in range(self.snake_num):
            self.snakes.append(Snake(i, random.randint(0, self.width - 1), random.randint(0, self.height - 1),
                                     "rlud"[random.randint(0, 3)], World.COLORS[i]))

    def is_head_out(self, head):
        i = head[0]
        j = head[1]
        return (i == -1 or
                i == self.width or
                j == -1 or
                j == self.height)

    def update_table(self):
        for snake in self.snakes:
            self.table[snake.snake_id] = (snake.color, snake.score)

    def collision_bodies(self, head):
        for snake in self.snakes:
            for body in snake.body:
                if body[0] == head[0] and body[1] == head[1]:
                    return True
        return False

    def is_dead(self, snake):
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if abs(i) + abs(j) != 1:
                    continue
                new_head = [snake.get_head()[0] + i, snake.get_head()[1] + j]
                if not self.is_head_out(new_head) and not self.collision_bodies(new_head):
                    return False
        return True

    def move_snake(self, snake, new_direction=None):

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

    def fix_action(self, snake):
        res = ""
        snake_dir = snake.direction
        while True:
            head = snake.get_head()

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

            if not self.is_head_out(head) and not self.collision_bodies(head):
                break
        return res

    def start(self, ai, simulation_mode=False):
        if not simulation_mode:
            cursor.hide()
            os.system("clear")
            print()
        while True:
            if self.cycle > self.cycles:
                break
            if not simulation_mode:
                render(self)
            new_snakes = []
            for snake in self.snakes:
                if self.is_dead(snake):
                    continue
                snake.direction = ai.get_action(snake)
                snake.direction = self.fix_action(snake)
                self.move_snake(snake)
                new_snakes.append(snake)

            if len(new_snakes) == 0:
                break
            self.snakes = new_snakes
            self.update_table()
            self.cycle = self.cycle + 1
            if not simulation_mode:
                time.sleep(0.5)
        if not simulation_mode:
            input()
        else:
            for snake in self.snakes:
                print(snake.score)
