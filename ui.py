from colored import fg, bg, attr
from copy import deepcopy

boxing = "┴┬│─┼└┘┐┌┤├"
bg_color = "grey_19"


def format_world(world):
    data = []
    boxing_data = []

    color_template = [
        ["white", "yellow", "light_yellow"],
        ["white", "white", "white"],
    ]
    bg_color_template = [
        [bg_color, bg_color, bg_color],
        [bg_color, bg_color, bg_color],
    ]
    boxing_color_template = (
        [bg_color, bg_color, bg_color],
        [bg_color, bg_color],
    )

    for row in world.scores:
        data_row = []
        bx_row = []
        for score in row:
            bx_row.append(deepcopy(boxing_color_template))
            if score == 0:
                data_row.append(([
                                     [" ", " ", " "],
                                     [" ", " ", " "],
                                 ], deepcopy(color_template), deepcopy(bg_color_template)))
            elif score < 10:
                data_row.append(([
                                     [" ", " ", str(score)],
                                     [" ", " ", " "],
                                 ], deepcopy(color_template), deepcopy(bg_color_template)))
            else:
                data_row.append(([
                                     [" ", str(int(score / 10)), str(score % 10)],
                                     [" ", " ", " "],
                                 ], deepcopy(color_template), deepcopy(bg_color_template)))
        boxing_data.append(bx_row)
        data.append(data_row)

    for snake in world.snakes:
        for body in snake.body:
            for i in range(2):
                for j in range(3):
                    data[body[1]][body[0]][2][i][j] = snake.color
        body = snake.get_head()
        for i in range(2):
            for j in range(3):
                data[body[1]][body[0]][2][i][j] = "light_" + snake.color

        for i in range(len(snake.body) - 1):
            cur = snake.body[i]
            nxt = snake.body[i + 1]

            if cur[0] == nxt[0]:
                for ii in range(3):
                    boxing_data[min(cur[1], nxt[1])][cur[0]][0][ii] = snake.color
            else:
                for ii in range(2):
                    boxing_data[cur[1]][max(cur[0], nxt[0])][1][ii] = snake.color

    return data, boxing_data


def render(world):
    data, boxing_color = format_world(world)
    n = len(data)
    m = len(data[0])
    hh = len(data[0][0][0])
    ww = len(data[0][0][0][0])

    print(world.cycle)
    print("%s%s%s" % (bg(bg_color), boxing[8], attr("reset")), end="")
    for i in range(m - 1):
        for i in range(ww):
            print("%s%s%s" % (bg(bg_color), boxing[3], attr("reset")), end="")
        print("%s%s%s" % (bg(bg_color), boxing[1], attr("reset")), end="")

    for i in range(ww):
        print("%s%s%s" % (bg(bg_color), boxing[3], attr("reset")), end="")
    print("%s%s%s" % (bg(bg_color), boxing[7], attr("reset")))

    for i in range(n - 1):
        for y in range(hh):
            for j in range(m):
                print("%s%s%s" % (bg(boxing_color[i][j][1][y]), boxing[2], attr("reset")), end="")
                for x in range(ww):
                    print("%s%s%s%s" % (bg(data[i][j][2][y][x]), fg(data[i][j][1][y][x]), data[i][j][0][y][x], attr("reset")), end="")
            print("%s%s%s" % (bg(bg_color), boxing[2], attr("reset")))

        print("%s%s%s" % (bg(bg_color), boxing[10], attr("reset")), end="")
        for ii in range(m - 1):
            for iii in range(ww):
                print("%s%s%s" % (bg(boxing_color[i][ii][0][iii]), boxing[3], attr("reset")), end="")
            print("%s%s%s" % (bg(bg_color), boxing[4], attr("reset")), end="")
        for ii in range(ww):
            print("%s%s%s" % (bg(boxing_color[i][m - 1][0][ii]), boxing[3], attr("reset")), end="")
        print("%s%s%s" % (bg(bg_color), boxing[9], attr("reset")))

    for y in range(hh):
        for i in range(m):
            print("%s%s%s" % (bg(boxing_color[n - 1][i][1][y]), boxing[2], attr("reset")), end="")
            for x in range(ww):
                print("%s%s%s%s" % (bg(data[n - 1][i][2][y][x]), fg(data[n - 1][i][1][y][x]), data[n - 1][i][0][y][x], attr("reset")), end="")
        print("%s%s%s" % (bg(bg_color), boxing[2], attr("reset")))

    print("%s%s%s" % (bg(bg_color), boxing[5], attr("reset")), end="")
    for i in range(m - 1):
        for i in range(ww):
            print("%s%s%s" % (bg(bg_color), boxing[3], attr("reset")), end="")
        print("%s%s%s" % (bg(bg_color), boxing[0], attr("reset")), end="")
    for i in range(ww):
        print("%s%s%s" % (bg(bg_color), boxing[3], attr("reset")), end="")
    print("%s%s%s" % (bg(bg_color), boxing[6], attr("reset")))
    for snake_id, score in world.table.items():
        print("%s%s%s" % (fg("light_" + score[0]), score[1], attr("reset")), "\t", end="")
    print()
    print("\033[%d;%dH" % (0, 0))

print([(i, v) for i, v in enumerate(boxing)])