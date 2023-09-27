#pragma once


#include "QtNodes/NodeDelegateModel"


namespace Atlas::Nodes::Common::Model {


    template<typename DataType>
    class Reduce : public QtNodes::NodeDelegateModel {
        private:
            std::vector<std::shared_ptr<DataType>> _inputs;  ///< the inputs
            std::shared_ptr<DataType> _output;  ///< the output

            /**
             * @brief reduce function to use with the std::reduce function
             * @param data_a the first data
             * @param data_b the second data
             * @return the reduced value
             * @note this function should be overriden by the child class
             */
            virtual std::shared_ptr<DataType> _reduce_function(
                    [[maybe_unused]] const std::shared_ptr<DataType>& data_a,
                    [[maybe_unused]] const std::shared_ptr<DataType>& data_b
            ) = 0;

        public:
            Reduce() = default;
            ~Reduce() override = default;

            /// @copydoc QtNodes::NodeDelegateModel::nPorts
            [[nodiscard]] unsigned int nPorts(QtNodes::PortType portType) const override {
                // a reduce function always have an additional input, and only a single output
                return portType == QtNodes::PortType::In ? this->_inputs.size() + 1 : 1;
            }

            /// @copydoc QtNodes::NodeDelegateModel::dataType
            [[nodiscard]] QtNodes::NodeDataType dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const override {
                return DataType().type();
            }

            /// @copydoc QtNodes::NodeDelegateModel::setInData
            void setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) override {
                // convert the data to the correct type
                std::shared_ptr<DataType> casted_data = std::dynamic_pointer_cast<DataType>(data);

                // save it to the inputs
                if (portIndex >= this->_inputs.size()) this->_inputs.push_back(casted_data);
                else this->_inputs[portIndex] = casted_data;

                // re-compute the output
                this->compute();
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

            /**
            * @brief check if the inputs are valid
            * @return true if the inputs are valid, false otherwise
            */
            bool check() {
                // only valid if all the inputs are valid
                return std::all_of(
                        this->_inputs.begin(),
                        this->_inputs.end(),
                        [](const std::shared_ptr<DataType>& input) -> bool { return input != nullptr; }
                );
            }

            /**
             * @brief compute the output data
             */
            void compute() {
                // check if the inputs are valid
                if (!this->check()) return;

                // compute the new output
                this->_output = std::reduce(
                        this->_inputs.begin() + 1,
                        this->_inputs.end(),
                        this->_inputs.at(0),
                        [this](
                                const std::shared_ptr<DataType>& data_a,
                                const std::shared_ptr<DataType>& data_b
                        ) -> std::shared_ptr<DataType> {
                            return this->_reduce_function(data_a, data_b);
                        }
                );

                // update the next nodes
                Q_EMIT dataUpdated(0);
            }
    };


}