#include "Atlas/nodes/decimal/model/division.h"


using namespace Atlas::Nodes::Decimal::Model;
using namespace Atlas::Nodes;


[[nodiscard]] QString Division::name() const {
    return QStringLiteral("Division");
}
[[nodiscard]] QString Division::caption() const {
    return QStringLiteral("Division");
}

std::shared_ptr<Decimal::Data> Division::_reduce_function(
        const std::shared_ptr<Decimal::Data>& data_a,
        const std::shared_ptr<Decimal::Data>& data_b
) {
    return std::make_shared<Decimal::Data>(data_a->value() / data_b->value());
}

