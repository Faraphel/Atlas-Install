#include <QApplication>
#include <QPushButton>
#include <QMenuBar>
#include <QVBoxLayout>

#include "QtNodes/NodeDelegateModelRegistry"
#include "QtNodes/GraphicsView"
#include "QtNodes/DataFlowGraphicsScene"
#include "QtNodes/DataFlowGraphModel"

#include "Atlas/nodes/decimal/data.h"
#include "Atlas/nodes/decimal/model/constant.h"
#include "Atlas/nodes/decimal/model/addition.h"
#include "Atlas/nodes/decimal/model/subtraction.h"
#include "Atlas/nodes/decimal/model/multiplication.h"
#include "Atlas/nodes/decimal/model/division.h"
#include "Atlas/nodes/variant/model/display.h"
#include "Atlas/nodes/decimal/model/to_variant.h"


using namespace Atlas;


int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    // initialise the registry
    std::shared_ptr<QtNodes::NodeDelegateModelRegistry> registry = std::make_shared<QtNodes::NodeDelegateModelRegistry>();
    registry->registerModel<Nodes::Decimal::Model::Constant>(QStringLiteral("Decimal"));
    registry->registerModel<Nodes::Decimal::Model::Addition>(QStringLiteral("Decimal"));
    registry->registerModel<Nodes::Decimal::Model::Subtraction>(QStringLiteral("Decimal"));
    registry->registerModel<Nodes::Decimal::Model::Multiplication>(QStringLiteral("Decimal"));
    registry->registerModel<Nodes::Decimal::Model::Division>(QStringLiteral("Decimal"));
    registry->registerModel<Nodes::Decimal::Model::ToVariant>(QStringLiteral("Decimal"));
    registry->registerModel<Nodes::Variant::Model::Display>(QStringLiteral("Variant"));

    // TEST
    QWidget mainWidget;

    auto menuBar = new QMenuBar();
    QMenu *menu = menuBar->addMenu("File");
    auto saveAction = menu->addAction("Save Scene");
    auto loadAction = menu->addAction("Load Scene");

    auto *layout = new QVBoxLayout(&mainWidget);

    QtNodes::DataFlowGraphModel dataFlowGraphModel(registry);

    layout->addWidget(menuBar);
    auto scene = new QtNodes::DataFlowGraphicsScene(dataFlowGraphModel, &mainWidget);

    auto view = new QtNodes::GraphicsView(scene);
    layout->addWidget(view);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);

    QObject::connect(
            saveAction,
            &QAction::triggered,
            scene,
            &QtNodes::DataFlowGraphicsScene::save
    );
    QObject::connect(
            loadAction,
            &QAction::triggered,
            scene,
            &QtNodes::DataFlowGraphicsScene::load
    );
    QObject::connect(
            scene,
            &QtNodes::DataFlowGraphicsScene::sceneLoaded,
            view,
            &QtNodes::GraphicsView::centerScene
    );

    mainWidget.setWindowTitle("Atlas-Install");
    mainWidget.resize(800, 600);
    mainWidget.showNormal();

    // start the App
    return QApplication::exec();
}
