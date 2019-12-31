#include <string>
#include <vector>
#include <cmath>
#include "json.hpp"

namespace alphabeta {

using Point = std::pair<int, int>;

struct Snake {
    int id;
    std::vector<Point> body;
    std::size_t length;
    bool growing;
};

int x(const Point& p) {
    return p.first;
}

int y(const Point& p) {
    return p.second;
}

enum class Direction {
    LEFT,
    RIGHT,
    UP,
    DOWN
};

char to_char(const Direction& dir) {
    switch(dir) {
        case Direction::LEFT:
            return 'l';
        case Direction::RIGHT:
            return 'r';
        case Direction::DOWN:
            return 'd';
        case Direction::UP:
            return 'u';
    }
}

class State {

public:

    int width;
    int height;
    std::vector<std::vector<int>> scores;
    std::vector<Snake> snakes;

    State()
    : width(0)
    , height(0)
    {}

    void from_json(const nlohmann::json& world_json) {
        this->height = world_json["height"];
        this->width = world_json["widht"];

        for (int h = 0; h < this->height; ++h) {
            this->scores.emplace_back();
            for (int w = 0; w < this->width; ++w)
                this->scores.back().emplace_back(world_json[h * this->width + w]);
        }

        for (auto&& snake : world_json["snakes"]) {
            this->snakes.push_back({snake["id"], {}, snake["length"], snake["growing"]});
            for (auto&& body : snake["body"]) {
                this->snakes.back().body.emplace_back(body["x"], body["y"]);
            }
        }
    }

};

const Point& get_head(const Snake& snake) {
    return snake.body.back();
}

bool is_head_out(int width, int height, const Point& head) {
    int i = x(head);
    int j = y(head);
    return (i == -1 ||
            i == width ||
            j == -1 ||
            j == height);
}

bool collision_bodies(const std::vector<Snake>& snakes, const Point& head) {
    for (auto&& snake : snakes) {
        for (auto&& body : snake.body)
            if (x(body) == x(head) and y(body) == y(head))
                return true;
        return false;
    }
}

bool is_dead(const State& state, int snake_id) {
    constexpr std::array<int, 3> direction = {-1, 0, 1};
    for (int i : direction)
        for (int j : direction) {
            if (std::abs(i) + std::abs(j) != 1)
                continue;
            auto new_head = Point{x(get_head(state.snakes[snake_id])) + i, y(get_head(state.snakes[snake_id])) + j};
            if (!is_head_out(state.width, state.height, new_head) && !collision_bodies(state.snakes, new_head))
                return false;
        }
    return true;
}

auto get_next_head(const Point& head, const Direction& action) {
    Point new_head{0, 0};
    switch(action) {
        case Direction::LEFT:
            new_head = Point{x(head) - 1, y(head)};
            break;
        case Direction::RIGHT:
            new_head = Point{x(head) + 1, y(head)};
            break;
        case Direction::DOWN:
            new_head = Point{x(head), y(head) + 1};
            break;
        case Direction::UP:
            new_head = Point{x(head), y(head) - 1};
            break;
    }
    return new_head;
}

bool is_action_available(const State& state, int snake_id, const Direction& action) {
    auto&& head = get_head(state.snakes[snake_id]);
    Point new_head = get_next_head(head, action);
    return !is_head_out(state.width, state.height, head) && !collision_bodies(state.snakes, new_head);
}

auto get_available_actions(const State& state, int snake_id) {
    constexpr std::array<Direction, 4> directions = {Direction::LEFT, Direction::RIGHT, Direction::UP, Direction::DOWN};
    std::vector<Direction> res;
    for (auto&& act : directions)
        if (is_action_available(state, snake_id, act))
            res.emplace_back(act);
    return res;
}

auto next_state(const State& state, int snake_id, const Direction& action) {
    auto new_state = state;

    auto& snake = new_state.snakes[snake_id];
    auto&& head = get_head(snake);

    if (snake.body.size() == 1) {
        if (new_state.scores[y(head)][x(head)] != 0) {
            snake.length = new_state.scores[y(head)][x(head)];
            new_state.scores[y(head)][x(head)] = 0;
            snake.growing = true;
        }
    } else
        if (snake.body.size() == snake.length)
            snake.growing = false;

    auto new_head = get_next_head(head, action);
    snake.body.push_back(new_head);
    if (!snake.growing) {
        snake.body.erase(snake.body.begin());
        if (snake.body.size() > 1)
            snake.body.erase(snake.body.begin());
    }


    return new_state;
}

std::string get_action(std::string world_json) {
    auto world = nlohmann::json::parse(world_json);
    return "r";
}

}
