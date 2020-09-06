# Copyright (C) 2020 Fondazione Istituto Italiano di Tecnologia
# Licensed under the MIT License https://opensource.org/licenses/MIT

cmake_minimum_required(VERSION 3.12)

# The version scheme of drake-lite-cmake follows the corresponding
# version of the used drake version, plus an additional version number
# that indicates drake-lite-cmake revision, i.e. drake-lite-cmake x.y.z.w is the w-release
# of drake-lite-cmake based on drake x.y.z
set(DRAKE_UPSTREAM_VERSION 0.18.0)
set(DRAKE_LITE_CMAKE_REVISION 0)
set(DRAKE_LITE_CMAKE_VERSION "${DRAKE_UPSTREAM_VERSION}.${DRAKE_LITE_CMAKE_REVISION}")
if(NOT DEFINED DRAKE_UPSTREAM_TAG)
  set(DRAKE_UPSTREAM_TAG "v${DRAKE_UPSTREAM_VERSION}")
endif()

project(drake-lite-cmake VERSION ${DRAKE_LITE_CMAKE_VERSION}
                         LANGUAGES C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/extern/ycm-0.11)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})

# Control where libraries and executables are placed during the build.
# With the following settings executables are placed in <the top level of the
# build tree>/bin and libraries/archives in <top level of the build tree>/lib.
# This is particularly useful to run ctests on libraries built on Windows
# machines: tests, which are executables, are placed in the same folders of
# dlls, which are treated as executables as well, so that they can properly
# find the libraries to run. This is a because of missing RPATH on Windows.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")

# Under MSVC, we set CMAKE_DEBUG_POSTFIX to "d" to add a trailing "d" to library
# built in debug mode. In this Windows user can compile, build and install the
# library in both Release and Debug configuration avoiding naming clashes in the
# installation directories.
if(MSVC)
  set(CMAKE_DEBUG_POSTFIX "d")
endif()

# On Windows, we only support compiling with toolset ClangCl
if(CMAKE_GENERATOR MATCHES "Visual Studio")
  if(NOT CMAKE_GENERATOR_TOOLSET MATCHES "ClangCl")
    message(WARNING "On Visual Studio, only the ClangCl toolset is currently supported. Please configure the CMake project specifying the ClangCl toolset.")
  endif()
endif()

include(FetchContent)
# Options
option(BUILD_SHARED_LIBS "If on, build shared libraries, otherwise build static libraries." ON)
option(DRAKE_LITE_CMAKE_GENERATE_SOURCE_FILES "Enable this option to regenerate the source_files.cmake file (requires to have all the Drake dependencies installed)" OFF)
option(DRAKE_LITE_CMAKE_USE_EXTERNAL_FCL "Enable this option to find a suitable fcl in the system with find_package, instead of using the internal one." OFF)
# If the library is compiled as shared, ensure  that static libraries are compiled with -fPIC
if(BUILD_SHARED_LIBS)
  set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)
endif()
option(BUILD_TESTING "Create tests using CMake" OFF)
if(BUILD_TESTING)
    enable_testing()
endif()

# To build shared libraries in Windows, we set CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS to TRUE.
# See https://cmake.org/cmake/help/v3.4/variable/CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS.html
# See https://blog.kitware.com/create-dlls-on-windows-without-declspec-using-new-cmake-export-all-feature/
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Encourage user to specify a build type (e.g. Release, Debug, etc.), otherwise set it to Release.
if(NOT CMAKE_CONFIGURATION_TYPES)
  if(NOT CMAKE_BUILD_TYPE)
    message(STATUS "Setting build type to 'Release' as none was specified.")
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY VALUE "Release")
  endif()
endif()

# Dependencies

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

find_package(Eigen3 3.3.4 CONFIG REQUIRED)
find_package(fmt 6.0 CONFIG REQUIRED)
find_package(spdlog 1.3 CONFIG REQUIRED)

find_package(tinyxml2 REQUIRED)
find_package(sdformat9 REQUIRED)

if(DRAKE_LITE_CMAKE_USE_EXTERNAL_FCL)
  find_package(fcl REQUIRED)
else()
  FetchContent_Declare(
    fcl
    GIT_REPOSITORY https://github.com/flexible-collision-library/fcl.git
    GIT_TAG        0d98b836d57b1a4f457fac8e52d6b22b56e5fdbf
  )
  FetchContent_GetProperties(fcl)
  if(NOT fcl_POPULATED)
    FetchContent_Populate(fcl)
    # Disable fcl tests even if drake-lite-cmake has BUILD_TESTING enabled
    set(DLC_BUILD_TESTING_BACKUP ${BUILD_TESTING})
    set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
    add_subdirectory(${fcl_SOURCE_DIR} ${fcl_BINARY_DIR})
    set(BUILD_TESTING ${DLC_BUILD_TESTING_BACKUP} CACHE BOOL "" FORCE)
  endif()
endif()


# tinyobjloader
FetchContent_Declare(
  tinyobjloader
  GIT_REPOSITORY https://github.com/tinyobjloader/tinyobjloader.git
  GIT_TAG        v1.0.6
)
FetchContent_GetProperties(tinyobjloader)
if(NOT tinyobjloader_POPULATED)
  FetchContent_Populate(tinyobjloader)
  set(TINYOBJLOADER_USE_DOUBLE ON CACHE BOOL "" FORCE)
  add_subdirectory(${tinyobjloader_SOURCE_DIR} ${tinyobjloader_BINARY_DIR})
endif()

# ghc/filesystem
FetchContent_Declare(
  ghcfilesystem
  GIT_REPOSITORY https://github.com/gulrak/filesystem.git
  GIT_TAG        v1.2.8
)
FetchContent_GetProperties(ghcfilesystem)
if(NOT ghcfilesystem_POPULATED)
  FetchContent_Populate(ghcfilesystem)
  set(GHC_FILESYSTEM_WITH_INSTALL OFF CACHE BOOL "" FORCE)
  add_subdirectory(${ghcfilesystem_SOURCE_DIR} ${ghcfilesystem_BINARY_DIR})
endif()

if(BUILD_TESTING)
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        release-1.8.1
  )

  FetchContent_GetProperties(googletest)
  if(NOT googletest_POPULATED)
    FetchContent_Populate(googletest)
    add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
  endif()
endif()

# Download drake source code using FetchContent
FetchContent_Declare(drake
                     GIT_REPOSITORY https://github.com/RobotLocomotion/drake.git
                     GIT_TAG        ${DRAKE_UPSTREAM_TAG})

FetchContent_GetProperties(drake)
if(NOT drake_POPULATED)
  message(STATUS "Downloading drake repo.")
  FetchContent_Populate(drake)

  # The include paths in drake assume that the repository is cloned in subdirectory called drake, and
  # that is not possible for the stock FetchContent, so we symlink (or copy) the content in a directory
  # called drake_CORRECTED_SOURCE_DIR
  set(drake_CORRECTED_SOURCE_DIR ${CMAKE_CURRENT_BINARY_DIR}/drake)
  set(drake_CORRECTED_PARENT_SOURCE_DIR ${CMAKE_CURRENT_BINARY_DIR})
  if(NOT WIN32)
    set(DRAKE_CMAKE_SYMBOLIC_LINK_SUPPORTED ON)
  else()
    set(DRAKE_CMAKE_SYMBOLIC_LINK_SUPPORTED OFF)
  endif()

  if(DRAKE_CMAKE_SYMBOLIC_LINK_SUPPORTED)
    if(NOT IS_DIRECTORY ${drake_CORRECTED_SOURCE_DIR})
      file(CREATE_LINK ${drake_SOURCE_DIR} ${drake_CORRECTED_SOURCE_DIR} SYMBOLIC)
    endif()
  else()
    file(REMOVE_RECURSE ${drake_CORRECTED_SOURCE_DIR})
    file(COPY ${drake_SOURCE_DIR} DESTINATION ${drake_CORRECTED_PARENT_SOURCE_DIR})
    file(RENAME ${drake_CORRECTED_PARENT_SOURCE_DIR}/drake-src ${drake_CORRECTED_SOURCE_DIR})
  endif()

  # Add list of sources that have been autogenerated from the bazel build scripts, for a new release
  if(DRAKE_LITE_CMAKE_GENERATE_SOURCE_FILES)
    include(GenerateSourceFiles)
  endif()

  include(autogenerated/source_files.cmake)

  # Remove black-listed source files
  # This files are brought in by targets that link common:common,
  # but they are not actually used in the core libraries, just in examples and tests
  list(REMOVE_ITEM SOURCE_FILES common/find_runfiles.h)
  list(REMOVE_ITEM SOURCE_FILES common/find_runfiles.cc)
  list(REMOVE_ITEM SOURCE_FILES common/find_resource.h)
  list(REMOVE_ITEM SOURCE_FILES common/find_resource.cc)
  list(REMOVE_ITEM SOURCE_FILES common/find_loaded_library.h)
  list(REMOVE_ITEM SOURCE_FILES common/find_loaded_library.cc)
  
  # temp_directory is Unix-only for now
  list(REMOVE_ITEM SOURCE_FILES common/temp_directory.h)
  list(REMOVE_ITEM SOURCE_FILES common/temp_directory.cc)
  
  # for drake_path.cc, we remove it but we also add a dummy version later
  list(REMOVE_ITEM SOURCE_FILES common/drake_path.hh)
  list(REMOVE_ITEM SOURCE_FILES common/drake_path.cc)

  # Append path to the list of files
  set(ABS_SOURCE_FILES "")
  foreach(file IN LISTS SOURCE_FILES)
    list(APPEND ABS_SOURCE_FILES "${drake_CORRECTED_SOURCE_DIR}/${file}")
  endforeach()
  
  # Add dummy_drake_path.cc
  list(APPEND ABS_SOURCE_FILES "${CMAKE_CURRENT_SOURCE_DIR}/dummy_drake_path.cc")

  add_library(drake-lite-cmake ${ABS_SOURCE_FILES})
  add_library(drake-lite-cmake::drake-lite-cmake ALIAS drake-lite-cmake)
  target_include_directories(drake-lite-cmake PUBLIC "$<BUILD_INTERFACE:${drake_CORRECTED_PARENT_SOURCE_DIR}>"
                                                     "$<INSTALL_INTERFACE:$<INSTALL_PREFIX>/${CMAKE_INSTALL_INCLUDEDIR}>")
  target_link_libraries(drake-lite-cmake PUBLIC Eigen3::Eigen fmt::fmt fcl
                                         PRIVATE ghc_filesystem tinyobjloader_double sdformat9::sdformat9 tinyxml2::tinyxml2 spdlog::spdlog)
  target_compile_features(drake-lite-cmake PUBLIC cxx_std_17)
  target_compile_definitions(drake-lite-cmake PRIVATE TINYOBJLOADER_USE_DOUBLE)
  target_compile_definitions(drake-lite-cmake PRIVATE HAVE_SPDLOG)

  if(MSVC)
    # Support for M_PI and for std::aligned_storage<Len, Align> with extended alignement
    target_compile_definitions(drake-lite-cmake PUBLIC _USE_MATH_DEFINES _ENABLE_EXTENDED_ALIGNED_STORAGE)

    # Disable harmless warnings
    target_compile_options(drake-lite-cmake PRIVATE /wd4068 /wd4244 /wd4267 /wd4275 /wd4996)

    # Enable /bigobj support
    target_compile_options(drake-lite-cmake PRIVATE /bigobj)
  endif()

  # Install headers
  foreach(abs_file IN LISTS ABS_SOURCE_FILES)
    if(abs_file MATCHES ".*\.h$")
      # Get absolute directory path
      get_filename_component(abs_dir ${abs_file} DIRECTORY)
      # Get relative directory path
      string(REPLACE "${drake_CORRECTED_SOURCE_DIR}/" "" rel_dir ${abs_dir})
      # Install header in correct directory
      install(FILES ${abs_file} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/drake/${rel_dir})
    endif()
  endforeach()


  # Install library
  include(GNUInstallDirs)
  install(TARGETS drake-lite-cmake
          EXPORT  ${PROJECT_NAME}
          LIBRARY       DESTINATION "${CMAKE_INSTALL_LIBDIR}"
          ARCHIVE       DESTINATION "${CMAKE_INSTALL_LIBDIR}"
          RUNTIME       DESTINATION "${CMAKE_INSTALL_BINDIR}")


  # Workaround for https://github.com/flexible-collision-library/fcl/issues/449
  find_package(ccd QUIET CONFIG)
  if(TARGET ccd)
    set(CCD_DEPENDENCY ccd)
  else()
    set(CCD_DEPENDENCY)
  endif()
  find_package(octomap QUIET CONFIG)
  if(TARGET octomap)
    set(OCTOMAP_DEPENDENCY octomap)
  else()
    set(OCTOMAP_DEPENDENCY)
  endif()


  # Install CMake package
  include(InstallBasicPackageFiles)
  install_basic_package_files(${PROJECT_NAME}
                              VERSION ${${PROJECT_NAME}_VERSION}
                              COMPATIBILITY AnyNewerVersion
                              NO_CHECK_REQUIRED_COMPONENTS_MACRO
                              DEPENDENCIES ${CCD_DEPENDENCY} ${OCTOMAP_DEPENDENCY} Eigen3 fmt fcl
                              PRIVATE_DEPENDENCIES sdformat9 spdlog tinyxml2)

  # Add uninstall target
  include(AddUninstallTarget)

  # Handle tests
  if(BUILD_TESTING)
    add_subdirectory(tests)
  endif()
endif()


