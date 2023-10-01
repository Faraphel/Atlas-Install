#pragma once


#include "QtNodes/NodeDelegateModel"
#include "Atlas/nodes/node/decimal/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Decimal::Model {


    class Absolute : public QtNodes::NodeDelegateModel {
        Q_OBJECT

    private:
        std::shared_ptr<Decimal::Data> _output;  ///< the output

    public:
        [[nodiscard]] QString name() const override;

        [[nodiscard]] QString caption() const override;

        [[nodiscard]] unsigned int nPorts(QtNodes::PortType portType) const override;

        [[nodiscard]] QtNodes::NodeDataType dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const override;

        void setInData(std::shared_ptr<QtNodes::NodeData> nodeData, QtNodes::PortIndex portIndex) override;

        std::shared_ptr<QtNodes::NodeData> outData(QtNodes::PortIndex port) override;

        QWidget *embeddedWidget() override;
    };


}