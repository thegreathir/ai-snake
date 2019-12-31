cmake_minimum_required(VERSION 3.10)
project(cppagent)

set (CMAKE_CXX_STANDARD 14)

find_package(PythonLibs 3 REQUIRED)
find_package(Boost COMPONENTS python37)

include_directories(${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})

python_add_module(cppagent cppagent.cpp)
target_link_libraries(cppagent ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
