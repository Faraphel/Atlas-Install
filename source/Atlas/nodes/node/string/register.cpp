#include <Atlas/nodes/node/string/register.h>


#include "Atlas/nodes/node/string/data.h"
#include "Atlas/nodes/node/string/model/constant.h"
#include "Atlas/nodes/node/string/model/to_variant.h"


using namespace Atlas::Nodes::String;


void Atlas::Nodes::String::register_all(const std::shared_ptr<QtNodes::NodeDelegateModelRegistry>& registry) {
    QString category = Data().type().name;

    registry->registerModel<Model::Constant>(category);
    registry->registerModel<Model::ToVariant>(category);
}
