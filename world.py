import json
import random
import time
import datetime
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

class Side:
    COLORS = ["red", "green", "blue", "magneta", "cyan"]
    A = 0
    B = 1

    @staticmethod
    def get_side(snake_id):
        if snake_id % 2 == 0:
            return Side.A
        return Side.B
    @staticmethod
    def get_color(side):
        if side == Side.A:
            return Side.COLORS[0]
        return Side.COLORS[2]

class Snake:

    def __init__(self, snake_id, x, y, direction):
        self.body = [(x, y)]
        self.score = 0
        self.direction = direction
        self.length = 1
        self.growing = False
        self.snake_id = snake_id
        self.side = Side.get_side(self.snake_id)
        self.color = Side.get_color(self.side)

    def get_head(self):
        return self.body[-1]


class World:

    def __init__(self, json_config=None):
        self.target_score = 500
        self.height = 12
        self.width = 40
        self.min_score = 0
        self.max_score = 9
        self.score_c = 10
        self.max_cycles = 1000
        self.cycle = 0
        self.eat_score = 5
        self.turn_cost = 1
        self.persist_score = False
        self.scores = []
        self.table = {}
        self.team_score = {}
        self.last_id = 0
        self.interval = 1000
        self.simulation_mode = False

        if json_config is not None:
            self.load_config(json_config)

        bg = BaitGenerator(self.width, self.height, "mapfile.txt")
        self.scores = bg.get_random(self.min_score, self.max_score)

        self.snakes = []
        self.agents = {}

    def is_head_out(self, head):
        i = head[0]
        j = head[1]
        return (i == -1 or
                i == self.width or
                j == -1 or
                j == self.height)

    def update_table(self):
        a_score = 0
        b_score = 0
        for snake in self.snakes:
            if snake.side == Side.A:
                a_score += snake.score
            if snake.side == Side.B:
                b_score += snake.score
            self.table[snake.snake_id] = (snake.color, snake.score)

        self.team_score[Side.A] = (Side.get_color(Side.A), a_score)
        self.team_score[Side.B] = (Side.get_color(Side.B), b_score)

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

    def tick(self):
        start_point = datetime.datetime.now()
        if self.cycle > self.max_cycles:
            return False

        if not self.simulation_mode:
            render(self)
        new_snakes = []
        for snake in self.snakes:
            if self.is_dead(snake):
                continue
            new_dir = self.agents[snake.snake_id].get_action(self)
            fixed_dir = self.fix_action(snake, new_dir)
            self.move_snake(snake, fixed_dir)
            new_snakes.append(snake)

        if len(new_snakes) == 0:
            return False
        self.snakes = new_snakes
        self.update_table()
        self.cycle = self.cycle + 1

        max_score = max(map((lambda v: v[1][1]), self.team_score.items()))

        if not self.simulation_mode:
            diff = (datetime.datetime.now() - start_point)
            diff = diff / datetime.timedelta(milliseconds=1)
            if diff < (self.interval * 2):
                time.sleep(((self.interval * 2) - diff) / 1000)

        if max_score >= self.target_score:
            if not self.simulation_mode:
                render(self)
            return False

        return True

    def start(self):
        if not self.simulation_mode:
            cursor.hide()
            os.system("clear")
            print()
        try:
            while True:
                if not self.tick():
                    break
        except KeyboardInterrupt:
            if not self.simulation_mode:
                os.system("clear")
                print()
                render(self)

        if not self.simulation_mode:
            cursor.show()
            input()
            os.system("clear")
        else:
            for snake in self.snakes:
                print(snake.score, self.cycle)

    def load_config(self, json_config):
        self.target_score = json_config.get("target_score", self.target_score)
        self.height = json_config.get("height", self.height)
        self.width = json_config.get("width", self.width)
        self.min_score = json_config.get("min_score", self.min_score)
        self.max_score = json_config.get("max_score", self.max_score)
        self.score_c = json_config.get("a", self.score_c)
        self.max_cycles = json_config.get("max_cycles", self.max_cycles)
        self.eat_score = json_config.get("b", self.eat_score)
        self.turn_cost = json_config.get("turn_cost", self.turn_cost)
        self.persist_score = json_config.get("persist_score", self.persist_score)
        self.interval = json_config.get("interval", self.interval)
        self.simulation_mode = json_config.get("simulation_mode", False)

    def to_json(self, snake_id):
        res = dict()
        res["height"] = self.height
        res["width"] = self.width
        res["scores"] = []

        for row in self.scores:
            for i in row:
                res["scores"].append(i)

        res["snakes"] = []

        for snake in self.snakes:
            res["snakes"].append({"id":snake.snake_id, "length":snake.length,
                "growing":snake.growing, "body":[], "side":snake.side})
            for body in snake.body:
                res["snakes"][-1]["body"].append({"x":body[0], "y":body[1]})

        res["my_snake_id"] = snake_id

        return json.dumps(res)

    def register(self, agent):
        new_id = self.last_id
        self.last_id = self.last_id + 1
        self.agents[new_id] = agent

        self.snakes.append(Snake(new_id, random.randint(0, self.width - 1), random.randint(0, self.height - 1),
                                 "rlud"[random.randint(0, 3)]))
        return new_id
