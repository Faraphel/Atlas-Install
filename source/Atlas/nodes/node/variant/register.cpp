#include <Atlas/nodes/node/variant/register.h>


#include "Atlas/nodes/node/variant/model/from_variant.h"
#include "Atlas/nodes/node/variant/model/display.h"
#include "Atlas/nodes/node/variant/data.h"


using namespace Atlas::Nodes::Variant;


void Atlas::Nodes::Variant::register_all(const std::shared_ptr<QtNodes::NodeDelegateModelRegistry>& registry) {
    QString category = Data().type().name;

    registry->registerModel<Model::FromVariant>(category);
    registry->registerModel<Model::Display>(category);
}