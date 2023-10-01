#pragma once


#include "QtNodes/NodeData"


namespace Atlas::Nodes::Base {

    /**
     * @brief an abstract data type
     * @details this class is used to store data
     */
    class Data : public QtNodes::NodeData {
        public:
            /**
             * @brief Returns the representation of the data
             * @return The representation of the data
             */
            [[nodiscard]] virtual QString text() const = 0;
    };


}
