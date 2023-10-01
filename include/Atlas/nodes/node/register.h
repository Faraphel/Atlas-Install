#pragma once


#include <memory>
#include "QtNodes/NodeDelegateModelRegistry"


namespace Atlas::Nodes {
    /// @brief registers all the models
    /// @param registry the registry to register the models to
    void register_all(const std::shared_ptr<QtNodes::NodeDelegateModelRegistry>& registry);
}
