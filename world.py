import json
import random
import time
import cursor
import os

from ui import render
from bait_generator import BaitGenerator

class Direction:
    RIGHT = "r"
    LEFT = "l"
    UP = "u"
    DOWN = "d"

    @staticmethod
    def get_all():
        return [Direction.UP, Direction.RIGHT, Direction.LEFT, Direction.DOWN]


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

    def __init__(self, config_file=None):
        self.target_score = 500
        self.height = 12
        self.width = 40
        self.min_score = 0
        self.max_score = 9
        self.score_c = 10
        self.snake_num = 1
        self.max_cycles = 1000
        self.cycle = 0
        self.eat_score = 5
        self.turn_cost = 1
        self.persist_score = False

        self.scores = []
        self.table = {}

        if config_file != None:
            self.load_config(config_file)

        bg = BaitGenerator(self.width, self.height, "mapfile.txt")
        self.scores = bg.get_scores()

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
            if self.scores[head[1]][head[0]] != 0:
                snake.score += self.score_c * self.scores[head[1]][head[0]] + self.eat_score
                snake.length = self.scores[head[1]][head[0]] + 1
                if not self.persist_score:
                    self.scores[head[1]][head[0]] = 0
                snake.growing = True
        else:
            if len(snake.body) == snake.length:
                snake.growing = False

        direction = snake.direction
        if new_direction:
            if snake.direction != new_direction:
                snake.score -= self.turn_cost
                snake.score = max(0, snake.score)
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
            if len(snake.body) > 1:
                snake.body.pop(0)
        snake.direction = direction

    def fix_action(self, snake, snake_dir):
        res = ""
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
            if self.cycle > self.max_cycles:
                break

            if not simulation_mode:
                render(self)
            new_snakes = []
            for snake in self.snakes:
                if self.is_dead(snake):
                    continue
                new_dir = ai.get_action(snake)
                # todo die
                fixed_dir = self.fix_action(snake, new_dir)
                self.move_snake(snake, fixed_dir)
                new_snakes.append(snake)

            if len(new_snakes) == 0:
                break
            self.snakes = new_snakes
            self.update_table()
            self.cycle = self.cycle + 1

            max_score = max(map(lambda x: x.score, self.snakes))

            if max_score >= self.target_score:
                if not simulation_mode:
                    render(self)
                break

            if not simulation_mode:
                time.sleep(0.25)
        if not simulation_mode:
            print('end')
            input()
        else:
            for snake in self.snakes:
                print(snake.score, self.cycle)

    def load_config(self, config_file):
        f = open(config_file, "r")
        json_config = json.loads(f.read())
        self.target_score = json_config.get("target_score", self.target_score)
        self.height = json_config.get("height", self.height)
        self.width = json_config.get("width", self.width)
        self.min_score = json_config.get("min_score", self.min_score)
        self.max_score = json_config.get("max_score", self.max_score)
        self.score_c = json_config.get("a", self.score_c)
        self.snake_num = json_config.get("snake_num", self.snake_num)
        self.max_cycles = json_config.get("max_cycles", self.max_cycles)
        self.eat_score = json_config.get("b", self.eat_score)
        self.turn_cost = json_config.get("turn_cost", self.turn_cost)
        self.persist_score = json_config.get("persist_score", self.persist_score)
