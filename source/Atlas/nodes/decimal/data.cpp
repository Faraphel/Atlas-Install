#include "Atlas/nodes/decimal/data.h"


using namespace Atlas::Nodes::Decimal;



Data::Data() : _value(0.0) {}
Data::Data(double value) : _value(value) {}

[[nodiscard]] double Data::value() const {
    return this->_value;
}

[[nodiscard]] QtNodes::NodeDataType Data::type() const {
    return QtNodes::NodeDataType("decimal", "Decimal");
}

QString Data::text() const {
    return QString::number(_value);
}
