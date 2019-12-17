from typing import Any
from queue import PriorityQueue
from copy import deepcopy
from world import *
import random
import json
import logging

logging.basicConfig(filename='gs.log', level=logging.DEBUG)
# logger = logging.getLogger('GS')


class SnakeWrapper(Snake):
    def __init__(self, snake: Snake):
        c = deepcopy(snake.__dict__)
        for key in c.keys():
            self.__dict__[key] = c[key]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class WorldWrapper(World):
    def __init__(self, world: World):
        super().__init__()
        c = deepcopy(world.__dict__)
        for key in c.keys():
            self.__dict__[key] = c[key]

        self.__dict__['snakes'] = [SnakeWrapper(snake)
                                   for snake in self.snakes]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def manhatan_distance(start, end):
    return abs(end[0] - start[0]) + abs(end[1] - start[1])


def get_opposit_dir(dir: Direction):
    if dir == Direction.UP:
        return Direction.DOWN
    if dir == Direction.DOWN:
        return Direction.UP
    if dir == Direction.RIGHT:
        return Direction.LEFT
    if dir == Direction.LEFT:
        return Direction.RIGHT


def get_available_moves(snake: SnakeWrapper):
    if snake.growing:
        res = 2 * snake.length - len(snake.body)
    else:
        res = len(snake.body)
    return min(res, 9)


class State:

    def __init__(self, world: WorldWrapper, prev, leading_action: Direction, snake: SnakeWrapper, path_len: int, target=None):
        self.world = WorldWrapper(world)
        self.prev = prev
        self.leading_action = leading_action
        self.target = target
        self.snake = SnakeWrapper(snake)
        self.path_len = path_len

    def get_next_by_action(self, direction: Direction) -> (WorldWrapper, Snake):
        new_world = deepcopy(self.world)
        new_snake = deepcopy(self.snake)
        new_world.move_snake(new_snake, direction)
        if self.world.is_head_out(new_snake.get_head()):
            return (None, None)
        return (WorldWrapper(new_world), SnakeWrapper(new_snake))

    def calc_h(self) -> int:
        head = self.snake.get_head()
        dist = manhatan_distance(head, self.target)
        return abs(get_available_moves(self.snake) - dist)

    def __eq__(self, other):
        if other == None:
            return False
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return self


class GS:
    def __init__(self, current_state: State, target):
        self.pq = PriorityQueue()
        self.mark = set()
        self.current_state = current_state
        self.target = target

        self.pq.put((-1, self.current_state))

    def build_path_to_goal(self):
        while(not self.pq.empty()):
            priority, top = self.pq.get()
            self.mark.add(top.snake.get_head())

            for dir in Direction.get_all():
                (neighbour, new_snake) = top.get_next_by_action(dir)
                if not neighbour or not new_snake:
                    continue
                if new_snake.get_head() in self.mark:
                    continue
                if len(self.current_state.snake.body) != 1 and dir == get_opposit_dir(top.snake.direction):
                    continue
                if top.path_len+1 > get_available_moves(new_snake):
                    continue
                ai_world = State(neighbour,
                                 top, dir, new_snake, top.path_len+1, self.target)
                self.pq.put((ai_world.calc_h(), ai_world))
                if self.target == new_snake.get_head():
                    return ai_world

    def get_next_move(self):

        goal_state = self.build_path_to_goal()

        if not goal_state:
            # logger.debug("goal_state is None")
            # logger.debug("snake len is: %d", len(
                # self.current_state.snake.body))
            # logger.debug("failed target %s with score: %d",
                         # str(self.target), self.current_state.world.scores[self.target[1]][self.target[0]])
            return None

        tmp = goal_state
        while tmp.path_len > 1:
            tmp = tmp.prev

        return tmp.leading_action


def find_goals(world, snake):
    m = (10000, None)
    all = list()
    for x in range(world.width):
        for y in range(world.height):
            dist = manhatan_distance((x, y), snake.get_head())
            if dist != 0 and dist <= get_available_moves(snake):
                all.append((world.scores[y][x], (x, y)))
                all.sort(key=lambda x: x[0])
    return all


def get_gs_action(world, snake):
    # logger.debug("-------------------------------------------")
    goals = find_goals(world, snake)
    # logger.debug("goals are: %s", str(goals))
    current_state = State(world, None, None, snake, 0)
    # logger.debug("head is at: %s", str(current_state.snake.get_head()))

    res = None
    for target in goals:
        res = GS(current_state, target[1]).get_next_move()
        if res is not None:
            return res

    return None
