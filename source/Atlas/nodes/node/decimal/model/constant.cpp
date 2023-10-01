#include <QtGui>
#include <iostream>

#include "Atlas/nodes/node/decimal/model/constant.h"


using namespace Atlas::Nodes::Decimal::Model;


Constant::Constant() {
    // initialise the line edit
    this->_lineEdit = new QLineEdit();
    this->_lineEdit->setValidator(new QDoubleValidator());
    QObject::connect(this->_lineEdit, &QLineEdit::textChanged, this, &Constant::refresh);
}


Constant::~Constant() {
    // delete the line edit
    delete this->_lineEdit;
}


QString Constant::name() const {
    return QStringLiteral("Constant");
}

QString Constant::caption() const {
    return QStringLiteral("Constant");
}

unsigned int Constant::nPorts(QtNodes::PortType port_type) const {
    return port_type == QtNodes::PortType::In ? 0 : 1;
}

[[nodiscard]] QtNodes::NodeDataType Constant::dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const {
    return Decimal::Data().type();
}

std::shared_ptr<QtNodes::NodeData> Constant::outData(QtNodes::PortIndex port) {
    return std::make_shared<Decimal::Data>(this->_value);
}

void Constant::setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) {
    Q_ASSERT(false && "No input, shouldn't be called");
}

void Constant::refresh() {
    this->_value = this->_lineEdit->text().toDouble();
    Q_EMIT dataUpdated(0);
}

QWidget* Constant::embeddedWidget() {
    return this->_lineEdit;
}
