#pragma once


#include "QtNodes/NodeDelegateModel"
#include <QLineEdit>
#include "Atlas/nodes/decimal/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Decimal::Model {


    class Constant : public QtNodes::NodeDelegateModel {
        Q_OBJECT

        public:
            Constant();
            ~Constant() override;

        /**
        * @brief the name of the node
        * @return the name of the node
        */
        [[nodiscard]] QString name() const override;
        /**
         * @brief the caption of the node
         * @return the caption of the node
         */
        [[nodiscard]] QString caption() const override;

        /**
         * @brief the number of ports the node has
         * @param portType the type of the port (input or output)
         * @return the number of ports the node has
         */
        [[nodiscard]] unsigned int nPorts(QtNodes::PortType portType) const override;
        /**
         * @brief the data type of the port
         * @param portType the type of the port (input or output)
         * @param portType the index of the port
         * @return the data type of the port
         */
        [[nodiscard]] QtNodes::NodeDataType dataType(QtNodes::PortType portType, QtNodes::PortIndex portIndex) const override;
        /**
         * @brief the output data of a port
         * @param port the index of the port
         * @return the output data of a port
         */
        std::shared_ptr<QtNodes::NodeData> outData(QtNodes::PortIndex port) override;

        /**
         * @brief set the input data of a port
         * @param data the input data
         * @param portIndex the index of the port
         */
        void setInData(std::shared_ptr<QtNodes::NodeData> data, QtNodes::PortIndex portIndex) override;

        /**
         * @brief refresh the node
         * @note this is called when the text in the line edit is changed
         */
        void refresh();

        /**
         * @brief get the embedded widget
         * @return the embedded widget
         */
        QWidget *embeddedWidget() override;

        protected:
            QLineEdit *_lineEdit;
            double _value = 0.0;
    };


}