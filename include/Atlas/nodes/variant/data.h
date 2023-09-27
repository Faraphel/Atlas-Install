#pragma once


#include <QtNodes/NodeData>
#include "Atlas/nodes/common/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Variant {


    /**
     * @brief the decimal data type
     * @details this class is used to store decimal data (double internally)
     */
    class Data : public Common::Data {
    protected:
        std::shared_ptr<Common::Data> _data;  //< a reference to a data object

    public:
        Data();
        explicit Data(const std::shared_ptr<Common::Data>& data);

        /**
         * @brief Returns the value of the data
         * @return the value of the data
         */
        [[nodiscard]] std::shared_ptr<Common::Data> value() const;

        /// @copydoc QtNodes::NodeData::type
        [[nodiscard]] QtNodes::NodeDataType type() const override;

        /// @copydoc Common::Data::text
        [[nodiscard]] QString text() const override;
    };


}
