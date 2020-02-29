# Copyright (C) 2020 Fondazione Istituto Italiano di Tecnologia
# Licensed under the MIT License https://opensource.org/licenses/MIT

cmake_minimum_required(VERSION 3.12)

project(drake-lite-cmake-external-examples)

# This project is an example of how both upstream drake and drake-lite-cmake can be
# consumed by a CMake project. As we do not want to duplicate drake examples, we assume
# that the drake source is available in the system, and is specified via the drake_SOURCE_DIR
# CMake enviroment
set(drake_SOURCE_DIR "" CACHE STRING "Location of the drake repo")
option(USE_DRAKE_LITE_CMAKE "If on, use drake-lite-cmake, otherwise use official drake." ON)

if(NOT IS_DIRECTORY ${drake_SOURCE_DIR})
  message(FATAL_ERROR "The CMake variable drake_SOURCE_DIR points to \"${drake_SOURCE_DIR}\" that is not an existing directory.")
endif()

if(USE_DRAKE_LITE_CMAKE)
  find_package(drake-lite-cmake REQUIRED)
  set(USED_DRAKE_LIBRARY drake-lite-cmake::drake-lite-cmake)
else()
  # See https://github.com/RobotLocomotion/drake-external-examples/tree/master/drake_cmake_installed
  find_package(drake CONFIG REQUIRED)
  set(USED_DRAKE_LIBRARY drake::drake)
endif()

# Avoid path names problems on Windows
file(TO_CMAKE_PATH ${drake_SOURCE_DIR} drake_SOURCE_DIR_CLEAN)

add_executable(simple_continuous_time_system ${drake_SOURCE_DIR_CLEAN}/examples/simple_continuous_time_system.cc)
target_link_libraries(simple_continuous_time_system PUBLIC ${USED_DRAKE_LIBRARY})
