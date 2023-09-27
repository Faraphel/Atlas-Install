#include "Atlas/nodes/decimal/model/subtraction.h"


using namespace Atlas::Nodes::Decimal::Model;
using namespace Atlas::Nodes;


[[nodiscard]] QString Subtraction::name() const {
    return QStringLiteral("Subtraction");
}
[[nodiscard]] QString Subtraction::caption() const {
    return QStringLiteral("Subtraction");
}

std::shared_ptr<Decimal::Data> Subtraction::_reduce_function(
        const std::shared_ptr<Decimal::Data>& data_a,
        const std::shared_ptr<Decimal::Data>& data_b
) {
    return std::make_shared<Decimal::Data>(data_a->value() - data_b->value());
}

