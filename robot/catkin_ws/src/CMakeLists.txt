# toplevel CMakeLists.txt for a catkin workspace
cmake_minimum_required(VERSION 3.0.2)

include(workspace.cmake OPTIONAL)
set(CATKIN_TOPLEVEL TRUE)

if(EXISTS "${CMAKE_SOURCE_DIR}/catkin/cmake/all.cmake" AND
   EXISTS "${CMAKE_SOURCE_DIR}/catkin/CMakeLists.txt")
  set(catkin_EXTRAS_DIR "${CMAKE_SOURCE_DIR}/catkin/cmake")
  include(catkin/cmake/all.cmake NO_POLICY_SCOPE)
  add_subdirectory(catkin)
else()
  if(NOT DEFINED CMAKE_PREFIX_PATH)
    if(NOT "$ENV{CMAKE_PREFIX_PATH}" STREQUAL "")
      string(REPLACE ":" ";" CMAKE_PREFIX_PATH $ENV{CMAKE_PREFIX_PATH})
    endif()
  endif()

  set(catkin_search_path "")
  foreach(path ${CMAKE_PREFIX_PATH})
    if(EXISTS "${path}/.CATKIN_WORKSPACE")
      list(FIND catkin_search_path ${path} _index)
      if(_index EQUAL -1)
        list(APPEND catkin_search_path ${path})
      endif()
    endif()
  endforeach()

  set(CATKIN_TOPLEVEL_FIND_PACKAGE TRUE)
  find_package(catkin REQUIRED
    NO_POLICY_SCOPE
    PATHS ${catkin_search_path}
    NO_DEFAULT_PATH NO_CMAKE_FIND_ROOT_PATH)
  unset(CATKIN_TOPLEVEL_FIND_PACKAGE)
endif()

catkin_workspace()
