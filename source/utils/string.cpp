#include <utils/string.h>

#include <regex>


std::string Utils::String::escape(const std::string& string) {
    return "\"" + std::regex_replace(string, std::regex("\""), "\\\"") + "\"";
}
