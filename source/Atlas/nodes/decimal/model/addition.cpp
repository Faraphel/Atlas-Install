#include "Atlas/nodes/decimal/model/addition.h"


using namespace Atlas::Nodes::Decimal::Model;
using namespace Atlas::Nodes;


[[nodiscard]] QString Addition::name() const {
    return QStringLiteral("Addition");
}
[[nodiscard]] QString Addition::caption() const {
    return QStringLiteral("Addition");
}

std::shared_ptr<Decimal::Data> Addition::_reduce_function(
        const std::shared_ptr<Decimal::Data>& data_a,
        const std::shared_ptr<Decimal::Data>& data_b
) {
    return std::make_shared<Decimal::Data>(data_a->value() + data_b->value());
}

