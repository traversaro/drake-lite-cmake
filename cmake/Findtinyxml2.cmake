# Copyright (C) 2020 Fondazione Istituto Italiano di Tecnologia
# Licensed under the MIT License https://opensource.org/licenses/MIT

#[=======================================================================[.rst:
Findtinyxml2
-------

Find tinyxml2.

Imported targets
^^^^^^^^^^^^^^^^

This module defines the following :prop_tgt:`IMPORTED` target:

``tinyxml2::tinyxml2``
  The tinyxml2 library, if found.

#]=======================================================================]

find_package(tinyxml2 QUIET CONFIG)

if(tinyxml2_FOUND AND TARGET tinyxml2::tinyxml2)
  return()
endif()

find_path(tinyxml2_INCLUDE_DIR tinyxml2.h)

find_library(tinyxml2_LIBRARY_RELEASE NAMES tinyxml2 libtinyxml2)
find_library(tinyxml2_LIBRARY_DEBUG NAMES tinyxml2d libtinyxml2d)
include(SelectLibraryConfigurations)
select_library_configurations(tinyxml2)
mark_as_advanced(tinyxml2_INCLUDE_DIR tinyxml2_LIBRARY_RELEASE tinyxml2_LIBRARY_DEBUG)

if(tinyxml2_INCLUDE_DIR AND tinyxml2_LIBRARY_RELEASE)
  if(NOT TARGET tinyxml2::tinyxml2)
    add_library(tinyxml2::tinyxml2 UNKNOWN IMPORTED)
    set_target_properties(tinyxml2::tinyxml2 PROPERTIES
      INTERFACE_INCLUDE_DIRECTORIES "${tinyxml2_INCLUDE_DIRS}")
    if(EXISTS "${tinyxml2_LIBRARY_RELEASE}")
      set_property(TARGET tinyxml2::tinyxml2 APPEND PROPERTY
        IMPORTED_CONFIGURATIONS RELEASE)
      set_target_properties(tinyxml2::tinyxml2 PROPERTIES
        IMPORTED_LOCATION_RELEASE "${tinyxml2_LIBRARY_RELEASE}")
    endif()
    if(EXISTS "${tinyxml2_LIBRARY_DEBUG}")
      set_property(TARGET tinyxml2::tinyxml2 APPEND PROPERTY
        IMPORTED_CONFIGURATIONS DEBUG)
      set_target_properties(tinyxml2::tinyxml2 PROPERTIES
        IMPORTED_LOCATION_DEBUG "${tinyxml2_LIBRARY_DEBUG}")
    endif()
  endif()
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(tinyxml2
                                  REQUIRED_VARS tinyxml2_INCLUDE_DIR tinyxml2_LIBRARY_RELEASE)
