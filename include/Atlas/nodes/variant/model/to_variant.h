#pragma once


#include "QtNodes/NodeDelegateModel"
#include <Atlas/nodes/variant/data.h>


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Variant::Model {


    template<typename DataInputType>
    class ToVariant : public QtNodes::NodeDelegateModel {
        private:
            std::shared_ptr<DataInputType> _input;  ///< the input
            std::shared_ptr<Variant::Data> _output;  ///< the output

        public:
            ToVariant() = default;
            ~ToVariant() override = default;

            /// @copydoc QtNodes::NodeDelegateModel::nPorts
            [[nodiscard]] unsigned int nPorts(QtNodes::PortType portType) const override {
                // a "to_variant" function only has one input and one output
                return 1;
            }

            /// @copydoc QtNodes::NodeDelegateModel::dataType
            [[nodiscard]] QtNodes::NodeDataType dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const override {
                return portType == QtNodes::PortType::In ? DataInputType().type() : Variant::Data().type();
            }

            /// @copydoc QtNodes::NodeDelegateModel::setInData
            void setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) override {
                // convert the data to the correct type
                std::shared_ptr<DataInputType> casted_data = std::dynamic_pointer_cast<DataInputType>(data);
                // update the input
                this->_output = std::make_shared<Variant::Data>(casted_data);
                // update the next nodes
                Q_EMIT dataUpdated(0);
            }

            /// @copydoc QtNodes::NodeDelegateModel::outData
            std::shared_ptr<QtNodes::NodeData> outData(QtNodes::PortIndex portIndex) override {
                // return the last computed output
                return this->_output;
            }

            /// @copydoc QtNodes::NodeDelegateModel::embeddedWidget
            QWidget *embeddedWidget() override {
                // reduced node doesn't have any embedded widget
                return nullptr;
            }
    };


}