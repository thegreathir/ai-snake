#include <string>
#include <vector>
#include <cmath>
#include <limits>
#include <random>
#include <memory>
#include "json.hpp"

namespace alphabeta {

class Config {

private:
    static std::unique_ptr<Config> instance;
    Config() = default;
public:
    bool persist_score;
    double turn_cost;
    double collision_cost;
    double decay_cost;
    double eat_score;
    double score_c;

    void load(const nlohmann::json& json_config) {
        this->persist_score = json_config["persist_score"];
        this->turn_cost = json_config["turn_cost"];
        this->collision_cost = json_config["collision_cost"];
        this->decay_cost = json_config["decay_cost"];
        this->eat_score = json_config["eat_score"];
        this->score_c = json_config["score_c"];
    }

    static const std::unique_ptr<Config>& i() {
        if (instance == nullptr)
            instance = std::unique_ptr<Config>(new Config());

        return instance;
    }
};

std::unique_ptr<Config> Config::instance = nullptr;

class Point {
    std::pair<int, int> coordinates;
public:
    int x() const {
        return coordinates.first;
    }
    int y() const {
        return coordinates.second;
    }
    Point(int x, int y)
    : coordinates(x, y)
    {}
};

enum class Direction : char {
    LEFT = 'l',
    RIGHT = 'r',
    UP = 'u',
    DOWN = 'd',
    NONE = 'n'
};

Direction to_direction(const std::string& c) {
    switch (c[0]) {
        case 'l':
            return Direction::LEFT;
        case 'r':
            return Direction::RIGHT;
        case 'u':
            return Direction::UP;
        case 'd':
            return Direction::DOWN;
        default:
            return Direction::NONE;
    }
}

class Snake {
public:
    int id;
    std::vector<Point> body;
    std::size_t length;
    std::size_t score;
    Direction direction;
    bool growing;

    class MetaData {
    public:
        int eat_count;
        explicit MetaData(int eat_count)
        : eat_count(eat_count)
        {}

    };
    MetaData data;

    const Point& get_head() const {
        return body.back();
    }

    Snake(int id, std::size_t length, std::size_t score, const Direction& direction,
            bool growing, const MetaData& meta_data)
    : id(id)
    , length(length)
    , score(score)
    , direction(direction)
    , growing(growing)
    , data(meta_data)
    {
    }
};

class State {
public:

    int width;
    int height;
    int my_snake_id;
    std::vector<std::vector<std::uint8_t>> scores;
    std::vector<Snake> snakes;

    struct MetaData {
    };

    MetaData data;

    explicit State(const nlohmann::json& world_json)
    : width(world_json["width"])
    , height(world_json["height"])
    , my_snake_id(world_json["my_snake_id"])
    {
        for (int h = 0; h < this->height; ++h) {
            this->scores.emplace_back();
            for (int w = 0; w < this->width; ++w)
                this->scores.back().emplace_back(world_json["scores"][h * this->width + w]);
        }

        for (auto&& snake : world_json["snakes"]) {
            this->snakes.emplace_back(snake["id"], snake["length"], snake["score"], to_direction(snake["direction"]),
                    snake["growing"], Snake::MetaData(0));
            for (auto&& body : snake["body"]) {
                this->snakes.back().body.emplace_back(body["x"], body["y"]);
            }
        }
    }

    bool is_head_out(const Point& head) const {
        int i = head.x();
        int j = head.y();
        return (i == -1 ||
                i == width ||
                j == -1 ||
                j == height);
    }

    bool collision_bodies(const Point& head) const {
        for (auto&& snake : snakes) {
            for (auto&& body : snake.body)
                if (body.x() == head.x() && body.y() == head.y())
                    return true;
        }
        return false;
    }

    bool is_dead(int snake_id) const {
        constexpr std::array<int, 3> direction = {-1, 0, 1};
        for (int i : direction)
            for (int j : direction) {
                if (std::abs(i) + std::abs(j) != 1)
                    continue;
                auto new_head = Point{snakes[snake_id].get_head().x() + i,
                                      snakes[snake_id].get_head().y() + j};

                if (!is_head_out(new_head) &&
                    !collision_bodies(new_head))
                    return false;
            }
        return true;
    }

    static auto get_next_head(const Point& head, const Direction& action) {
        Point new_head{0, 0};
        switch (action) {
            case Direction::LEFT:
                new_head = Point{head.x() - 1, head.y()};
                break;
            case Direction::RIGHT:
                new_head = Point{head.x() + 1, head.y()};
                break;
            case Direction::DOWN:
                new_head = Point{head.x(), head.y() + 1};
                break;
            case Direction::UP:
                new_head = Point{head.x(), head.y() - 1};
                break;
            default:
                new_head = head;
                break;
        }
        return new_head;
    }

    bool is_action_available(int snake_id, const Direction& action) const {
        auto&& head = snakes[snake_id].get_head();
        Point new_head = get_next_head(head, action);
        return !is_head_out(head)
               && !collision_bodies(new_head);
    }

    auto get_available_actions(int snake_id) const {
        constexpr std::array<Direction, 4> directions = {Direction::LEFT,
                                                         Direction::RIGHT, Direction::UP, Direction::DOWN};
        std::vector<Direction> res;
        for (auto&& act : directions)
            if (is_action_available(snake_id, act))
                res.emplace_back(act);


        static auto rng = std::default_random_engine {};
        std::shuffle(std::begin(res), std::end(res), rng);
        return res;
    }
};

auto next_state(const State& state, int snake_id, const Direction& action) {
    auto new_state = state;

    auto& snake = new_state.snakes[snake_id];
    auto&& head = snake.get_head();

    if (snake.body.size() == 1) {
        if (new_state.scores[head.y()][head.x()] != 0) {
            snake.score = Config::i()->score_c * new_state.scores[head.y()][head.x()] + Config::i()->eat_score;
            snake.length = new_state.scores[head.y()][head.x()] + 1;
            snake.data.eat_count += 1;

            if (!Config::i()->persist_score)
                new_state.scores[head.y()][head.x()] = 0;
            snake.growing = true;
        }
    } else
        if (snake.body.size() == snake.length)
            snake.growing = false;

    if (action != snake.direction)
    {
        snake.score -= Config::i()->turn_cost;
        snake.score = std::max(0UL, snake.score);
    }

    auto new_head = alphabeta::State::get_next_head(head, action);
    snake.body.push_back(new_head);
    if (!snake.growing) {
        snake.body.erase(snake.body.begin());
        if (snake.body.size() > 1)
            snake.body.erase(snake.body.begin());
    }

    if (snake.body.size() == 1) {
        snake.score -= Config::i()->decay_cost;
        snake.score = std::max(0UL, snake.score);
    }

    snake.direction = action;

    return new_state;
}

double get_heuristic_value(const State& state, int /*snake_id*/) {
    double team_score = 0;
    for (auto&& snake : state.snakes)
        if ((state.my_snake_id % 2) == (snake.id % 2))
            team_score += static_cast<double>(snake.data.eat_count);
    return team_score;
}

std::pair<double, Direction> alphabeta(const State& state, int depth, double alpha, double beta,
        std::size_t snake_id, bool my_turn) {

    if (state.is_dead(snake_id)) {
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
        for (auto&& candidate : state.get_available_actions(snake_id)) {
            double new_val = 0;
            std::tie(new_val, std::ignore) = alphabeta(next_state(state, snake_id, candidate),
                    depth - 1, alpha, beta, (snake_id + 1) % state.snakes.size(), false);

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
        for (auto&& candidate : state.get_available_actions(snake_id)) {
            double new_val = 0;
            std::tie(new_val, std::ignore) = alphabeta(next_state(state, snake_id, candidate),
                    depth - 1, alpha, beta, (snake_id + 1) % state.snakes.size(), true);

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

char get_action(const std::string& world_json_string, int depth = 13) {
    auto world_json = nlohmann::json::parse(world_json_string);

    Config::i()->load(world_json);

    State state(world_json);
    Direction action = Direction::NONE;
    std::tie(std::ignore, action) = alphabeta(state, depth, -std::numeric_limits<double>::infinity(),
            std::numeric_limits<double>::infinity(), state.my_snake_id, true);

    return action == Direction::NONE ? 'l' : static_cast<char>(action);
}

}
