# Qt Nodes

# add the Qt Nodes library
add_subdirectory(nodeeditor)
# override the target properties for QtNodes
set_target_properties(QtNodes
        PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)
