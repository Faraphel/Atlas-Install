#pragma once

#include <iostream>

#include "QtNodes/NodeDelegateModel"
#include "Atlas/nodes/node/variant/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Variant::Model {


    class FromVariant : public QtNodes::NodeDelegateModel {
    private:
        std::shared_ptr<Variant::Data> _input;  ///< the input

    public:
        FromVariant() = default;
        ~FromVariant() override = default;

        /// @copydoc QtNodes::NodeDelegateModel::caption
        [[nodiscard]] QString caption() const override;

        /// @copydoc QtNodes::NodeDelegateModel::name
        [[nodiscard]] QString name() const override;

        /// @copydoc QtNodes::NodeDelegateModel::nPorts
        [[nodiscard]] unsigned int nPorts(QtNodes::PortType portType) const override;

        /// @copydoc QtNodes::NodeDelegateModel::dataType
        [[nodiscard]] QtNodes::NodeDataType dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const override;

        /// @copydoc QtNodes::NodeDelegateModel::setInData
        void setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) override;

        /// @copydoc QtNodes::NodeDelegateModel::outData
        std::shared_ptr<QtNodes::NodeData> outData(QtNodes::PortIndex portIndex) override;

        /// @copydoc QtNodes::NodeDelegateModel::embeddedWidget
        QWidget* embeddedWidget() override;
    };


}
