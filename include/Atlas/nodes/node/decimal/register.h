#pragma once


#include <memory>
#include "QtNodes/NodeDelegateModelRegistry"


namespace Atlas::Nodes::Decimal {
    /// @brief registers all the decimal models
    /// @param registry the registry to register the models to
    void register_all(const std::shared_ptr<QtNodes::NodeDelegateModelRegistry>& registry);
}
