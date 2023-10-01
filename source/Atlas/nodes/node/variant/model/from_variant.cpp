#include "Atlas/nodes/node/variant/model/from_variant.h"


using namespace Atlas::Nodes::Variant::Model;


[[nodiscard]] QString FromVariant::name() const {
    QString output_name = this->_input == nullptr ? QStringLiteral("...") : this->_input->value()->type().name;
    return QStringLiteral("Variant to ") + output_name;
}
[[nodiscard]] QString FromVariant::caption() const {
    QString output_name = this->_input == nullptr ? QStringLiteral("???") : this->_input->value()->type().name;
    return QStringLiteral("Variant to ") + output_name;
}

[[nodiscard]] unsigned int FromVariant::nPorts(QtNodes::PortType portType) const {
    // a "from_variant" function only has one input and one output only if the input is set
    return portType == QtNodes::PortType::In ? 1 : (this->_input == nullptr ? 0 : 1);
}

[[nodiscard]] QtNodes::NodeDataType FromVariant::dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const {
return portType == QtNodes::PortType::In ? Variant::Data().type() : this->_input->value()->type();
}

void FromVariant::setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) {
    // update the input
    this->_input = data == nullptr ? nullptr : std::dynamic_pointer_cast<Variant::Data>(data);
    // update the next nodes
    if (this->_input != nullptr) Q_EMIT dataUpdated(0);
}

std::shared_ptr<QtNodes::NodeData> FromVariant::outData(QtNodes::PortIndex portIndex) {
    // return the last computed output
    return this->_input->value();
}

QWidget* FromVariant::embeddedWidget() {
    // reduced node doesn't have any embedded widget
    return nullptr;
}
