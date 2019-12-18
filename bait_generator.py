import math
import random


class BaitGenerator():
    def __init__(self, x: int, y: int, filename='mapfile.txt'):
        self.x = x
        self.y = y
        self.filename = filename
        self.map_data = None

    def read_file(self):
        file = open(self.filename, 'r')
        local_y, local_x = [int(x) for x in file.readline().split()]

        self.map_data = list()
        for i in range(local_y):
            self.map_data.append([int(x) for x in file.readline().split()])
        file.close()

    def get_random(self, min_score, max_score):
        scores = []
        for i in range(self.y):
            row = []
            for j in range(self.x):
                row.append(random.randint(min_score, max_score))
            scores.append(row)
        return scores

    def get_scores(self):
        scores = []
        self.read_file()
        local_y = len(self.map_data)
        local_x = len(self.map_data[0])

        for i in range(self.y):
            scores.append([])

        for i in range(self.y):
            for j in range(self.x):
                scores[i].append(self.map_data[math.floor(
                    local_y * i / self.y)][math.floor(local_x * j / self.x)])

        return scores
