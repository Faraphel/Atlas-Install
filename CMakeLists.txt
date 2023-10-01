cmake_minimum_required(VERSION 3.26)
project(Atlas_Install)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(CMAKE_PREFIX_PATH "C:/Qt/6.5.2/mingw_64/lib/cmake")

# find Qt
find_package(Qt6 COMPONENTS
        Core
        Gui
        Widgets
        REQUIRED
)

# include the headers
include_directories(${PROJECT_SOURCE_DIR}/include)

# add external libraries
add_subdirectory(${PROJECT_SOURCE_DIR}/external)

# compile the program
add_executable(Atlas_Install
        source/main.cpp

        include/Atlas/nodes/node/register.h
        source/Atlas/nodes/node/register.cpp

        include/Atlas/nodes/node/base/model/reduce.h
        source/Atlas/nodes/node/base/model/reduce.cpp
        include/Atlas/nodes/node/base/data.h
        source/Atlas/nodes/node/base/data.cpp

        source/Atlas/nodes/node/decimal/data.cpp
        include/Atlas/nodes/node/decimal/data.h
        source/Atlas/nodes/node/decimal/model/constant.cpp
        include/Atlas/nodes/node/decimal/model/constant.h
        include/Atlas/nodes/node/decimal/model/addition.h
        source/Atlas/nodes/node/decimal/model/addition.cpp
        include/Atlas/nodes/node/decimal/model/subtraction.h
        source/Atlas/nodes/node/decimal/model/subtraction.cpp
        include/Atlas/nodes/node/decimal/model/multiplication.h
        source/Atlas/nodes/node/decimal/model/multiplication.cpp
        include/Atlas/nodes/node/decimal/model/division.h
        source/Atlas/nodes/node/decimal/model/division.cpp
        source/Atlas/nodes/node/decimal/model/to_variant.cpp
        include/Atlas/nodes/node/decimal/model/to_variant.h
        include/Atlas/nodes/node/decimal/model/absolute.h
        source/Atlas/nodes/node/decimal/model/absolute.cpp
        include/Atlas/nodes/node/decimal/register.h
        source/Atlas/nodes/node/decimal/register.cpp

        include/Atlas/nodes/node/variant/data.h
        source/Atlas/nodes/node/variant/data.cpp
        include/Atlas/nodes/node/variant/model/display.h
        source/Atlas/nodes/node/variant/model/display.cpp
        include/Atlas/nodes/node/variant/model/to_variant.h
        include/Atlas/nodes/node/variant/model/from_variant.h
        source/Atlas/nodes/node/variant/model/to_variant.cpp
        source/Atlas/nodes/node/variant/model/from_variant.cpp
        source/Atlas/nodes/node/variant/model/to_variant.cpp
        include/Atlas/nodes/node/variant/model/to_variant.h
        include/Atlas/nodes/node/variant/model/from_variant.h
        source/Atlas/nodes/node/variant/model/from_variant.cpp
        source/Atlas/nodes/node/variant/model/from_variant.cpp
        source/Atlas/nodes/node/variant/register.cpp
        include/Atlas/nodes/node/variant/register.h
        source/Atlas/nodes/node/string/register.cpp
        source/Atlas/nodes/node/string/data.cpp
        include/Atlas/nodes/node/string/model/constant.h
        source/Atlas/nodes/node/string/model/constant.cpp
        include/utils/string.h
        source/utils/string.cpp
)

target_link_libraries(Atlas_Install
        # Qt
        Qt::Core
        Qt::Gui
        Qt::Widgets
        # external libraries
        QtNodes
)

# copy Qt dlls
if (WIN32 AND NOT DEFINED CMAKE_TOOLCHAIN_FILE)

    set(DEBUG_SUFFIX)

    if (MSVC AND CMAKE_BUILD_TYPE MATCHES "Debug")
        set(DEBUG_SUFFIX "d")
    endif ()

    set(QT_INSTALL_PATH "${CMAKE_PREFIX_PATH}")

    if (NOT EXISTS "${QT_INSTALL_PATH}/bin")
        set(QT_INSTALL_PATH "${QT_INSTALL_PATH}/..")
        if (NOT EXISTS "${QT_INSTALL_PATH}/bin")
            set(QT_INSTALL_PATH "${QT_INSTALL_PATH}/..")
        endif ()
    endif ()

    if (EXISTS "${QT_INSTALL_PATH}/plugins/platforms/qwindows${DEBUG_SUFFIX}.dll")
        add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E make_directory
                "$<TARGET_FILE_DIR:${PROJECT_NAME}>/plugins/platforms/")
        add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy
                "${QT_INSTALL_PATH}/plugins/platforms/qwindows${DEBUG_SUFFIX}.dll"
                "$<TARGET_FILE_DIR:${PROJECT_NAME}>/plugins/platforms/")
    endif ()

    foreach (QT_LIB Core Gui Widgets)
        add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy
                "${QT_INSTALL_PATH}/bin/Qt6${QT_LIB}${DEBUG_SUFFIX}.dll"
                "$<TARGET_FILE_DIR:${PROJECT_NAME}>")
    endforeach (QT_LIB)

endif ()
