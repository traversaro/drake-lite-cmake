# Copyright (C) 2020 Fondazione Istituto Italiano di Tecnologia
# Licensed under the MIT License https://opensource.org/licenses/MIT

include(GoogleTest)

# This tests are hardcoded, so it may be possible that need to be changed from release to release
add_executable(bouncing_ball_test ${drake_CORRECTED_SOURCE_DIR}/examples/bouncing_ball/bouncing_ball.cc
                                  ${drake_CORRECTED_SOURCE_DIR}/examples/bouncing_ball/test/bouncing_ball_test.cc)
target_link_libraries(bouncing_ball_test PUBLIC drake-lite-cmake::drake-lite-cmake gtest gtest_main)
gtest_add_tests(TARGET bouncing_ball_test)
