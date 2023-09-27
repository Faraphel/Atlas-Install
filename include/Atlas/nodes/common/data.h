#pragma once


#include <QtNodes/NodeData>


namespace Atlas::Nodes::Common {

    /**
     * @brief the decimal data type
     * @details this class is used to store decimal data (double internally)
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
