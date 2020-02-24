# drake-lite-cmake

Reduced (lite) unofficial version of drake (https://drake.mit.edu/) that can be built with CMake.

**Disclaimer:** drake-lite-cmake is an independent and unofficial project and is not related by any means to Toyota Research Instiute and MIT.


# Overview
- [Background](#background)
- [Dependencies](#dependencies)
- [Build and link the library](#build-and-link-the-library)
- [Test the library](#test-the-library)
- [API Documentation](#api-documentation)


# Background
[`drake`](https://github.com/RobotLocomotion/drake) is a "collection of tools for analyzing the dynamics of our robots and building control systems for them, with a heavy emphasis on optimization-based design/analysis".
It is C++ library that contains unique features such as a [Simulink-inspired description of interconnected dynamical systems](https://drake.mit.edu/doxygen_cxx/group__systems.html) and [newly developed contact simulation algorithms specifically optimized for robot manipulation](https://drake.mit.edu/doxygen_cxx/group__contact__engineering.html).

However, it is currently (as of early 2020) [distributed upstream](https://drake.mit.edu/installation.html) only with all its features enabled,
requering the installation of [a large number of system packages](https://github.com/RobotLocomotion/drake-external-examples/tree/master/drake_cmake_installed), requiring the use of its own [vendored](https://stackoverflow.com/questions/26217488/what-is-vendoring) dependencies and supporting only a limited number of Operating Systems.

This repo contains a CMake script that builds an limited subset (lite) of Drake, using CMake to find or install dependencies, ensuring cross-platform compatibility and easy integration with existing CMake workflows.

The subset of Drake currently included is the one concerning the simulation of interconnected dynamical systems (`drake::systems` namespace) and the simulation of mechanical systems with contacts.
In particular, this subset depends just on `fmt`, `Eigen3`, `fcl` and other small self-contained C++ libraries.

All the parts of drake related to communication (that depends on the `lcm` library), Python bindings (the `pydrake` library) and that depend on proprietary dependency (such as the optimization infrastructure) are **not** part of `drake-lite-cmake`, and if you are interested in those you need to use the official Drake installing it from the [official instructions](https://drake.mit.edu/installation.html).

For check if your Drake-based code can work with `drake-lite-cmake`, compare the headers that you used in your code the exact headers included in each version of `drake-lite-cmake`, available in the release notes.

**Note that this is an unofficial and experimental project, and it provides no guarantees to work. In particular, if you find any problem using `drake-lite-cmake`, do not report them to drake upstream, as
the problem could be induced by the modifications done at the `drake-lite-cmake` level.**

# Dependencies
drake-lite-cmake depends on
 - [Eigen3](http://eigen.tuxfamily.org) - `version >= 3.3.3`
 - [Flexible Collision Library (fcl)](https://github.com/flexible-collision-library/fcl) - `version >= 0.6.0`
 - [fmt](https://fmt.dev) - `version >= 4.0.0`


# Build and link the library
Use the following commands to build, install and link the library, assuming that the required dependencies can be found by CMake.

### Build
With `make` facilities:
```bash
$ git clone https://github.com/traversaro/drake-lite-cmake
$ cd drake-lite-cmake
$ mkdir build && cd build
$ cmake ..
$ make
$ [sudo] make install
```

With IDE build tool facilities:
```bash
$ git clone https://github.com/traversaro/drake-lite-cmake
$ cd drake-lite-cmake
$ mkdir build && cd build
$ cmake ..
$ cmake --build . --target ALL_BUILD --config Release
$ cmake --build . --target INSTALL --config Release
```

See [CGold guide](https://cgold.readthedocs.io/en/latest/first-step.html) if you need more details on how to build a CMake project.

### Link
Once the library is installed, you can link it using `CMake` with as little effort as writing the following line of code in your project `CMakeLists.txt`:
```cmake
...
find_package(drake-lite-cmake REQUIRED)
...
target_link_libraries(<target> drake-lite-cmake::drake-lite-cmake)
...
```

# Test the library
`drake-lite-cmake` can run a sample of Drake's tests to make sure that the library is working correctly, to run them just enable the `BUILD_TESTING` CMake option, compile the project and run:
```sh
$ ctest [-VV]
```
to run all the tests.


# API documentaion
For API documentation, the users should refer to the official Drake documentation available at https://drake.mit.edu/, at least for the headers and the versions that are distributed with `drake-lite-cmake`.

