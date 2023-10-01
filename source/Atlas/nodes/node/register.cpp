#include "Atlas/nodes/node/register.h"

#include "Atlas/nodes/node/decimal/register.h"
#include "Atlas/nodes/node/string/register.h"
#include "Atlas/nodes/node/variant/register.h"


using namespace Atlas;


void Atlas::Nodes::register_all(const std::shared_ptr<QtNodes::NodeDelegateModelRegistry>& registry) {
    Nodes::Decimal::register_all(registry);
    Nodes::String::register_all(registry);
    Nodes::Variant::register_all(registry);
}