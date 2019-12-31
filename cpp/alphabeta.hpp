#include <string>
#include <iostream>
#include "json.hpp"

namespace alphabeta {

std::string get_action(std::string world_json) {
    auto world = nlohmann::json::parse(world_json);
    std::cout << world << std::endl;
    return "r";
}

}
