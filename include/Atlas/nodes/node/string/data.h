#pragma once

#include "QtNodes/NodeData"
#include "Atlas/nodes/node/base/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::String {

    /**
     * @brief the string data type
     * @details this class is used to store string data (std::string internally)
     */
    class Data : public Base::Data {
        protected:
            std::string _value;  //< the value of the data

        public:
            /**
             * @brief Default constructor
             * @details Use the default value
             */
            Data();
            /**
             * @brief Constructor
             * @param value The value to use
             */
            explicit Data(std::string value);

            /**
             * @brief Returns the value of the data
             * @return the value of the data
             */
            [[nodiscard]] std::string value() const;

            /// @copydoc QtNodes::NodeData::type
            [[nodiscard]] QtNodes::NodeDataType type() const override;

            /**
             * @brief Returns the representation of the data
             * @return The representation of the data
             */
            [[nodiscard]] QString text() const override;
    };


}
