from colored import fg, bg, attr
from copy import deepcopy

boxing = "┴┬│─┼└┘┐┌┤├"


def format(world):
    data = []

    color_template = [
        ["white", "yellow", "yellow"],
        ["white", "white", "white"],
        ["white", "white", "white"],
    ]

    for row in world.scores:
        data_row = []
        for score in row:
            if score == 0:
                data_row.append(([
                                     [" ", " ", " "],
                                     [" ", " ", " "],
                                     [" ", " ", " "],
                                 ], deepcopy(color_template)))
            elif score < 10:
                data_row.append(([
                                     [" ", " ", str(score)],
                                     [" ", " ", " "],
                                     [" ", " ", " "],
                                 ], deepcopy(color_template)))
            else:
                data_row.append(([
                                     [" ", str(int(score / 10)), str(score % 10)],
                                     [" ", " ", " "],
                                     [" ", " ", " "],
                                 ], deepcopy(color_template)))
        data.append(data_row)

    for snake in world.snakes:
        for body in snake.body:
            for i in range(2):
                for j in range(3):
                    data[body[1]][body[0]][0][1 + i][j] = "█"
                    data[body[1]][body[0]][1][1 + i][j] = snake.color
        body = snake.get_head()
        for i in range(2):
            for j in range(3):
                data[body[1]][body[0]][0][1 + i][j] = "█"
                data[body[1]][body[0]][1][1 + i][j] = "light_" + snake.color

    return data


def render(world):
    data = format(world)
    n = len(data)
    m = len(data[0])
    hh = len(data[0][0][0])
    ww = len(data[0][0][0][0])

    print(world.cycle)
    print(boxing[8], end="")
    for i in range(m - 1):
        for i in range(ww):
            print(boxing[3], end="")
        print(boxing[1], end="")

    for i in range(ww):
        print(boxing[3], end="")
    print(boxing[7])

    for i in range(n - 1):
        for y in range(hh):
            for j in range(m):
                print(boxing[2], end="")
                for x in range(ww):
                    print("%s%s%s" % (fg(data[i][j][1][y][x]), data[i][j][0][y][x], attr("reset")), end="")
            print(boxing[2])

        print(boxing[10], end="")
        for i in range(m - 1):
            for i in range(ww):
                print(boxing[3], end="")
            print(boxing[4], end="")
        for i in range(ww):
            print(boxing[3], end="")
        print(boxing[9])

    for y in range(hh):
        for i in range(m):
            print(boxing[2], end="")
            for x in range(ww):
                print("%s%s%s" % (fg(data[n - 1][i][1][y][x]), data[n - 1][i][0][y][x], attr("reset")), end="")
        print(boxing[2])

    print(boxing[5], end="")
    for i in range(m - 1):
        for i in range(ww):
            print(boxing[3], end="")
        print(boxing[0], end="")
    for i in range(ww):
        print(boxing[3], end="")
    print(boxing[6])
    for snake_id, score in world.table.items():
        print ("%s%s%s" % (fg("light_" + score[0]), score[1], attr("reset")), "\t", end="")
    print()
    print("\033[%d;%dH" % (0, 0))
