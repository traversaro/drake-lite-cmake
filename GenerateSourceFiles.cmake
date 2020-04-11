# Copyright (C) 2020 Fondazione Istituto Italiano di Tecnologia
# Licensed under the MIT License https://opensource.org/licenses/MIT

# .rst: GenerateSourceFiles
# -------------------------
#
# Help CMake script to generate the source files corresponding to a subset
# of drake, assuming that bazel and all dependencies of drake are installed.

find_package(Python COMPONENTS Interpreter REQUIRED)
# Generate the script source_files 
set(SOURCE_FILES_FILE "${PROJECT_SOURCE_DIR}/autogenerated/source_files.cmake")
# Bazel targets to include in drake-lite-cmake
set(BAZEL_TARGETS_TO_INCLUDE "//math //multibody/plant:plant //systems/analysis:simulator //systems/framework")
message(STATUS "Generating ${SOURCE_FILES_FILE} by running bazel.")
# Generate the actual command in a .sh script to avoid the strange execute_process limitations
file(WRITE 
     "${CMAKE_CURRENT_BINARY_DIR}/generate_source_files.sh" 
     "python3 ${PROJECT_SOURCE_DIR}/scripts/generate-source-files.py --targets ${BAZEL_TARGETS_TO_INCLUDE} --output ${SOURCE_FILES_FILE}\n")
execute_process(COMMAND sh ${CMAKE_CURRENT_BINARY_DIR}/generate_source_files.sh
                WORKING_DIRECTORY ${drake_SOURCE_DIR})
