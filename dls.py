from world import Direction

from copy import deepcopy


class State:
    def __init__(self):
        self.world_scores = []
        self.snake = []
        self.score = 0
        self.world = None
        self.growing = False
        self.length = 0
        self.catch_count = 0

    def from_world(self, world, snake):
        for row in world.scores:
            self.world_scores.append([])
            for score in row:
                self.world_scores[-1].append(score)
        for body in snake.body:
            self.snake.append(body)
        self.growing = snake.growing
        self.score = snake.score
        self.length = snake.length
        self.world = world
        self.catch_count = 0

    def is_head_out(self, head):
        i = head[0]
        j = head[1]
        return (i == -1 or
                i == self.world.width or
                j == -1 or
                j == self.world.height)

    def collision_bodies(self, head):
        for body in self.snake:
            if body[0] == head[0] and body[1] == head[1]:
                return True
        return False

    def is_dead(self):
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if abs(i) + abs(j) != 1:
                    continue
                new_head = [self.snake[-1][0] + i, self.snake[-1][1] + j]
                if not self.is_head_out(new_head) and not self.collision_bodies(new_head):
                    return False
        return True


def is_available(state, action):
    head = state.snake[-1]
    new_head = None
    if action == Direction.LEFT:
        new_head = (head[0] - 1, head[1])
    elif action == Direction.UP:
        new_head = (head[0], head[1] - 1)
    elif action == Direction.RIGHT:
        new_head = (head[0] + 1, head[1])
    elif action == Direction.DOWN:
        new_head = (head[0], head[1] + 1)
    if new_head is None:
        return False

    return not state.is_head_out(new_head) and not state.collision_bodies(new_head)


def get_available_actions(state):
    return [action for action in [Direction.RIGHT, Direction.LEFT, Direction.DOWN, Direction.UP] if
            is_available(state, action)]


def next_state(old_state, action):
    state = deepcopy(old_state)

    head = state.snake[-1]
    if len(state.snake) == 1:
        state.catch_count = state.catch_count + 1
        state.score += state.world.score_c * state.world_scores[head[1]][head[0]] + 1
        state.length = state.world_scores[head[1]][head[0]] + 1
        state.growing = True
    else:
        if len(state.snake) == state.length:
            state.growing = False

    nxt = None
    if action == Direction.RIGHT:
        nxt = (head[0] + 1, head[1])
    elif action == Direction.LEFT:
        nxt = (head[0] - 1, head[1])
    elif action == Direction.UP:
        nxt = (head[0], head[1] - 1)
    elif action == Direction.DOWN:
        nxt = (head[0], head[1] + 1)
    state.snake.append(nxt)
    if not state.growing:
        state.snake.pop(0)
        state.snake.pop(0)
    return state


def dls(state, limit):
    if limit == 0:
        return state.catch_count, None
    if state.is_dead():
        return -1, None
    actions = get_available_actions(state)

    children = []
    for action in actions:
        new_state = next_state(state, action)
        score, _ = dls(new_state, limit - 1)
        children.append((score, action))

    return max(children, key=lambda x: x[0])


def get_dls_action(world, snake):
    state = State()
    state.from_world(world, snake)

    return dls(state, 5)[1]
