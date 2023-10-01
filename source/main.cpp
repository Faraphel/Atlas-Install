#include <QApplication>
#include <QPushButton>
#include <QMenuBar>
#include <QVBoxLayout>

#include "QtNodes/NodeDelegateModelRegistry"
#include "QtNodes/GraphicsView"
#include "QtNodes/DataFlowGraphicsScene"
#include "QtNodes/DataFlowGraphModel"

#include "Atlas/nodes/node/register.h"


using namespace Atlas;


int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    // set up the registry
    std::shared_ptr<QtNodes::NodeDelegateModelRegistry> registry = std::make_shared<QtNodes::NodeDelegateModelRegistry>();
    // register all the models
    Nodes::register_all(registry);

    // set up the graph
    QtNodes::DataFlowGraphModel dataFlowGraphModel(registry);

    // TEST
    QWidget mainWidget;

    auto menuBar = new QMenuBar();
    QMenu *menu = menuBar->addMenu("File");
    auto saveAction = menu->addAction("Save Scene");
    auto loadAction = menu->addAction("Load Scene");

    auto *layout = new QVBoxLayout(&mainWidget);

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
