#pragma once


#include "Atlas/nodes/node/variant/model/to_variant.h"
#include "Atlas/nodes/node/string/data.h"


using namespace Atlas::Nodes;


namespace Atlas::Nodes::String::Model {


    class ToVariant : public Variant::Model::ToVariant<String::Data> {
        public:
            ToVariant() = default;
            ~ToVariant() override = default;
    };


}