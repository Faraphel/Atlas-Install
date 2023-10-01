#include <QtGui>
#include <iostream>

#include "Atlas/nodes/node/string/model/constant.h"


using namespace Atlas::Nodes::String;


Model::Constant::Constant() {
    // initialise the line edit
    this->_lineEdit = new QLineEdit();
    QObject::connect(this->_lineEdit, &QLineEdit::textChanged, this, &Constant::refresh);
}


Model::Constant::~Constant() {
    // delete the line edit
    delete this->_lineEdit;
}


QString Model::Constant::name() const {
    return Data().type().name + QStringLiteral("::Constant");
}

QString Model::Constant::caption() const {
    return QStringLiteral("Constant");
}

unsigned int Model::Constant::nPorts(QtNodes::PortType port_type) const {
    return port_type == QtNodes::PortType::In ? 0 : 1;
}

[[nodiscard]] QtNodes::NodeDataType Model::Constant::dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const {
    return String::Data().type();
}

std::shared_ptr<QtNodes::NodeData> Model::Constant::outData(QtNodes::PortIndex port) {
    return std::make_shared<String::Data>(this->_value);
}

void Model::Constant::setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) {
    Q_ASSERT(false && "No input, shouldn't be called");
}

void Model::Constant::refresh() {
    this->_value = this->_lineEdit->text().toStdString();  // TODO: use the NodeData type for string directory on this->_output
    Q_EMIT dataUpdated(0);
}

QWidget* Model::Constant::embeddedWidget() {
    return this->_lineEdit;
}
