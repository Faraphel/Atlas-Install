#pragma once


#include <Atlas/nodes/decimal/data.h>
#include <Atlas/nodes/variant/model/to_variant.h>


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Decimal::Model {


    class ToVariant : public Variant::Model::ToVariant<Decimal::Data> {
        Q_OBJECT

        public:
            [[nodiscard]] QString name() const override;

            [[nodiscard]] QString caption() const override;
    };


}
