#include "Atlas/nodes/node/decimal/model/multiplication.h"


using namespace Atlas::Nodes::Decimal::Model;
using namespace Atlas::Nodes;


[[nodiscard]] QString Multiplication::name() const {
    return QStringLiteral("Multiplication");
}
[[nodiscard]] QString Multiplication::caption() const {
    return QStringLiteral("Multiplication");
}

std::shared_ptr<Decimal::Data> Multiplication::_reduce_function(
        const std::shared_ptr<Decimal::Data>& data_a,
        const std::shared_ptr<Decimal::Data>& data_b
) {
    return std::make_shared<Decimal::Data>(data_a->value() * data_b->value());
}

