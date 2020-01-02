#include <string>
#include <vector>
#include <cmath>
#include <limits>
#include "json.hpp"

namespace alphabeta {

using Point = std::pair<int, int>;

struct Snake {
    int id;
    std::vector<Point> body;
    std::size_t length;
    bool growing;

    struct MetaData {
        int eat_count;
    };
    MetaData data;
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
    DOWN,
    NONE
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
        default:
            return 'l';
    }
}

class State {
public:

    int width;
    int height;
    int my_snake_id;
    int opp_snake_id;
    std::vector<std::vector<int>> scores;
    std::vector<Snake> snakes;

    struct MetaData {
    };

    MetaData data;

    void from_json(const nlohmann::json& world_json) {
        this->height = world_json["height"];
        this->width = world_json["width"];

        for (int h = 0; h < this->height; ++h) {
            this->scores.emplace_back();
            for (int w = 0; w < this->width; ++w)
                this->scores.back().emplace_back(world_json["scores"][h * this->width + w]);
        }

        for (auto&& snake : world_json["snakes"]) {
            this->snakes.push_back({snake["id"], {}, snake["length"],
                    snake["growing"], {0}});
            for (auto&& body : snake["body"]) {
                this->snakes.back().body.emplace_back(body["x"], body["y"]);
            }
        }

        this->my_snake_id = world_json["my_snake_id"];
        this->opp_snake_id = world_json["opp_snake_id"];
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
            if (x(body) == x(head) && y(body) == y(head))
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
            auto new_head = Point{x(get_head(state.snakes[snake_id])) + i,
                y(get_head(state.snakes[snake_id])) + j};

            if (!is_head_out(state.width, state.height, new_head) &&
                    !collision_bodies(state.snakes, new_head))
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
    return !is_head_out(state.width, state.height, head)
        && !collision_bodies(state.snakes, new_head);
}

auto get_available_actions(const State& state, int snake_id) {
    constexpr std::array<Direction, 4> directions = {Direction::LEFT,
        Direction::RIGHT, Direction::UP, Direction::DOWN};
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
            snake.data.eat_count += 1;
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

double get_heuristic_value(const State& state, int /*snake_id*/) {
    return static_cast<double>(state.snakes[state.my_snake_id].data.eat_count);
}

std::pair<double, Direction> alphabeta(const State& state, int depth, double alpha, double beta,
        bool my_turn) {
    int snake_id = my_turn ? state.my_snake_id : state.opp_snake_id; 

    if (is_dead(state, snake_id)) {
        if (my_turn) {
            return std::make_pair(-std::numeric_limits<double>::infinity(), Direction::NONE);
        } else {
            return std::make_pair(std::numeric_limits<double>::infinity(), Direction::NONE);
        }
    }

    if (depth == 0)
        return std::make_pair(get_heuristic_value(state, snake_id), Direction::NONE);

    if (my_turn) {
        double value = -std::numeric_limits<double>::infinity();
        Direction action = Direction::NONE;
        for (auto&& candidate : get_available_actions(state, snake_id)) {
            double new_val = 0;
            std::tie(new_val, std::ignore) = alphabeta(next_state(state, snake_id, candidate),
                    depth - 1, alpha, beta, false);

            if (new_val > value) {
                action = candidate;
                value = new_val;
            }

            alpha = std::max(alpha, value);
            if (alpha >= beta)
                break;
        }
        return std::make_pair(value, action);
    } else {
        double value = std::numeric_limits<double>::infinity();
        Direction action = Direction::NONE;
        for (auto&& candidate : get_available_actions(state, snake_id)) {
            double new_val = 0;
            std::tie(new_val, std::ignore) = alphabeta(next_state(state, snake_id, candidate),
                    depth - 1, alpha, beta, true);

            if (new_val < value) {
                action = candidate;
                value = new_val;
            }

            beta = std::min(beta, value);
            if (alpha >= beta)
                break;
        }
        return std::make_pair(value, action);
    }
}

char get_action(std::string world_json) {
    auto world = nlohmann::json::parse(world_json);

    State state;
    state.from_json(world);
    Direction action = Direction::NONE;
    constexpr int depth = 13;
    std::tie(std::ignore, action) = alphabeta(state, depth, -std::numeric_limits<double>::infinity(),
            std::numeric_limits<double>::infinity(), true);

    return to_char(action);
}

}
