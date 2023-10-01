#pragma once


#include "Atlas/nodes/node/variant/model/to_variant.h"
#include "Atlas/nodes/node/decimal/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::Decimal::Model {


    class ToVariant : public Variant::Model::ToVariant<Decimal::Data> {
        public:
            ToVariant() = default;
            ~ToVariant() override = default;
    };


}