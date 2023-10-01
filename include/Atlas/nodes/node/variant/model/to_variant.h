#pragma once


#include "QtNodes/NodeDelegateModel"
#include "Atlas/nodes/node/variant/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Variant::Model {


    template<typename NodeInputType>
    class ToVariant : public QtNodes::NodeDelegateModel {
        private:
            std::shared_ptr<Variant::Data> _output;  ///< the output

        public:
            ToVariant() = default;
            ~ToVariant() override = default;

            /// @copydoc QtNodes::NodeDelegateModel::name
            QString name() const override {
                return NodeInputType().type().name + QStringLiteral("::To Variant");
            }

            /// @copydoc QtNodes::NodeDelegateModel::caption
            QString caption() const override {
                return NodeInputType().type().name + QStringLiteral(" to Variant");
            }

            /// @copydoc QtNodes::NodeDelegateModel::nPorts
            [[nodiscard]] unsigned int nPorts(QtNodes::PortType portType) const override {
                // a "to_variant" function only has one input if the output is set and one output
                return portType == QtNodes::PortType::In ? 1 : 1;
            }

            /// @copydoc QtNodes::NodeDelegateModel::dataType
            [[nodiscard]] QtNodes::NodeDataType dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const override {
                return portType == QtNodes::PortType::In ? NodeInputType().type() : Variant::Data().type();
            }

            /// @copydoc QtNodes::NodeDelegateModel::setInData
            void setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) override {
                if (data == nullptr) {
                    // clear the output
                    this->_output = nullptr;
                } else {
                    // convert the data to the common type
                    std::shared_ptr<Base::Data> casted_data = std::dynamic_pointer_cast<Base::Data>(data);
                    // update the output
                    this->_output = std::make_shared<Variant::Data>(casted_data);
                }
                // update the next nodes
                Q_EMIT dataUpdated(0);
            }

            /// @copydoc QtNodes::NodeDelegateModel::outData
            std::shared_ptr<QtNodes::NodeData> outData(QtNodes::PortIndex portIndex) override {
                // return the last computed output
                return static_cast<const std::shared_ptr<QtNodes::NodeData> &>(this->_output);
            }

            /// @copydoc QtNodes::NodeDelegateModel::embeddedWidget
            QWidget *embeddedWidget() override {
                // reduced node doesn't have any embedded widget
                return nullptr;
            }
    };


}
