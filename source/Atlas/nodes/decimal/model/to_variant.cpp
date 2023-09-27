#include <Atlas/nodes/decimal/model/to_variant.h>


using namespace Atlas::Nodes::Decimal::Model;


[[nodiscard]] QString ToVariant::name() const {
    return QStringLiteral("Decimal to Variant");
}
[[nodiscard]] QString ToVariant::caption() const {
    return QStringLiteral("Decimal to Variant");
}
