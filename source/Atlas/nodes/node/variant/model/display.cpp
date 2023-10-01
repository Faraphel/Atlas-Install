#include "Atlas/nodes/node/variant/model/display.h"


using namespace Atlas::Nodes;
using namespace Atlas::Nodes::Variant::Model;


Display::Display() {
    this->_label = new QLabel();
}

Display::~Display() {
    delete this->_label;
}

QString Display::name() const {
    return QStringLiteral("Display");
}

QString Display::caption() const {
    return QStringLiteral("Display");
}

unsigned int Display::nPorts(QtNodes::PortType port_type) const {
    return port_type == QtNodes::PortType::In ? 1 : 0;
}

[[nodiscard]] QtNodes::NodeDataType Display::dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const {
    return Variant::Data().type();
}

std::shared_ptr<QtNodes::NodeData> Display::outData(QtNodes::PortIndex port) {
    Q_ASSERT(false && "No output, shouldn't be called");
}

void Display::setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) {
    // set the text of the label to the text of the data
    std::shared_ptr<Variant::Data> cast_data = std::dynamic_pointer_cast<Variant::Data>(data);

    this->_label->setText((cast_data == nullptr) ? "<Invalid>" : cast_data->text());
    this->_label->adjustSize();
}

QWidget* Display::embeddedWidget() {
    return this->_label;
}
