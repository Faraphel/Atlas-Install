#pragma once


#include <string>


namespace Utils::String {
    /// @brief escapes a string
    /// @details this function escapes a string so that it look like its c++ representation
    /// @param str the string to escape
    /// @return the escaped string
    std::string escape(const std::string& string);
}
