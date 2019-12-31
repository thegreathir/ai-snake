#include "alphabeta.hpp"
#include <boost/python.hpp>

BOOST_PYTHON_MODULE(cppagent)
{
    using namespace boost::python;
    def("get_action", alphabeta::get_action);
}
