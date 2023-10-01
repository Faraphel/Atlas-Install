#include <Atlas/nodes/node/decimal/model/absolute.h>


using namespace Atlas::Nodes::Decimal::Model;


QString Absolute::name() const {
    return QStringLiteral("Absolute");
}

QString Absolute::caption() const {
    return QStringLiteral("Absolute");
}

unsigned int Absolute::nPorts(QtNodes::PortType portType) const {
    return 1;
}

QtNodes::NodeDataType Absolute::dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const {
    return Decimal::Data().type();
}

void Absolute::setInData(std::shared_ptr<QtNodes::NodeData> nodeData, const QtNodes::PortIndex portIndex) {
    if (nodeData == nullptr) {
        this->_output = nullptr;
    } else {
        std::shared_ptr<Decimal::Data> casted_data = std::dynamic_pointer_cast<Decimal::Data>(nodeData);
        double value = std::abs(casted_data->value());
        this->_output = std::make_shared<Decimal::Data>(value);
    }

    Q_EMIT dataUpdated(0);
}

std::shared_ptr<QtNodes::NodeData> Absolute::outData(const QtNodes::PortIndex port) {
    return this->_output;
}

QWidget *Absolute::embeddedWidget() {
    return nullptr;
}
