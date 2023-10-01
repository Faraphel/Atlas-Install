#pragma once


#include "Atlas/nodes/node/decimal/data.h"
#include "Atlas/nodes/node/base/model/reduce.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Decimal::Model {


    class Addition : public Base::Model::Reduce<Decimal::Data> {
        Q_OBJECT

        private:
            std::shared_ptr<Decimal::Data> _reduce_function(
                    const std::shared_ptr<Decimal::Data>& data_a,
                    const std::shared_ptr<Decimal::Data>& data_b
            ) override;

        public:
            [[nodiscard]] QString name() const override;

            [[nodiscard]] QString caption() const override;
    };


}