#include <Atlas/nodes/variant/data.h>
#include <Atlas/nodes/decimal/data.h>


using namespace Atlas::Nodes::Variant;
using namespace Atlas::Nodes;


Data::Data() : _data(std::make_shared<Decimal::Data>(0.0)) {}  // TODO: make this a null data type
Data::Data(const std::shared_ptr<Common::Data>& data) : _data(data) {}

[[nodiscard]] std::shared_ptr<Common::Data> Data::value() const {
    return this->_data;
}

[[nodiscard]] QtNodes::NodeDataType Data::type() const {
    return QtNodes::NodeDataType("variant", "Variant");
}

QString Data::text() const {
    return this->_data->type().name + ": " + this->_data->text();
}