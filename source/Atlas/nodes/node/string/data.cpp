#include "Atlas/nodes/node/string/data.h"
#include "utils/string.h"


using namespace Atlas::Nodes::String;



Data::Data() : _value("") {}
Data::Data(std::string value) : _value(value) {}

[[nodiscard]] std::string Data::value() const {
    return this->_value;
}

[[nodiscard]] QtNodes::NodeDataType Data::type() const {
    return QtNodes::NodeDataType("string", "String");
}

QString Data::text() const {
    return QString::fromStdString(Utils::String::escape(this->_value));
}
