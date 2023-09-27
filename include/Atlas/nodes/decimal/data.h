#pragma once

#include "QtNodes/NodeData"
#include "Atlas/nodes/common/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Decimal {

    /**
     * @brief the decimal data type
     * @details this class is used to store decimal data (double internally)
     */
    class Data : public Common::Data {
        protected:
            double _value;  //< the value of the data

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
            explicit Data(double value);

            /**
             * @brief Returns the value of the data
             * @return the value of the data
             */
            [[nodiscard]] double value() const;

            /// @copydoc QtNodes::NodeData::type
            [[nodiscard]] QtNodes::NodeDataType type() const override;

            /**
             * @brief Returns the representation of the data
             * @return The representation of the data
             */
            [[nodiscard]] QString text() const override;
    };


}
