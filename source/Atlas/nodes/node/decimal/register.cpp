#include <Atlas/nodes/node/decimal/register.h>


#include "Atlas/nodes/node/decimal/model/constant.h"
#include "Atlas/nodes/node/decimal/model/to_variant.h"
#include "Atlas/nodes/node/decimal/model/addition.h"
#include "Atlas/nodes/node/decimal/model/subtraction.h"
#include "Atlas/nodes/node/decimal/model/multiplication.h"
#include "Atlas/nodes/node/decimal/model/division.h"
#include "Atlas/nodes/node/decimal/model/absolute.h"
#include "Atlas/nodes/node/decimal/data.h"


using namespace Atlas::Nodes::Decimal;


void Atlas::Nodes::Decimal::register_all(const std::shared_ptr<QtNodes::NodeDelegateModelRegistry>& registry) {
    QString category = Data().type().name;

    registry->registerModel<Model::Constant>(category);
    registry->registerModel<Model::ToVariant>(category);
    registry->registerModel<Model::Addition>(category);
    registry->registerModel<Model::Subtraction>(category);
    registry->registerModel<Model::Multiplication>(category);
    registry->registerModel<Model::Division>(category);
    registry->registerModel<Model::Absolute>(category);
}