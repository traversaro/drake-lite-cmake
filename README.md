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


# Build and use the library
Use the following commands to build, install and use the library, assuming that the required dependencies can be found by CMake.

## Linux/macOS 
First of all, install all the required dependencies, and make sure that can be found by CMake. 
For the dependencies installed by apt/homebrew this tipically happens automatically, while for manually installed 
depedencies you need to add the installation prefix to the [`CMAKE_PREFIX_PATH` enviroment variable](https://cmake.org/cmake/help/latest/variable/CMAKE_PREFIX_PATH.html).

Then you can compile and install `drake-lite-cmake` as:  
```bash
$ git clone https://github.com/traversaro/drake-lite-cmake
$ cd drake-lite-cmake
$ mkdir build && cd build
$ cmake -DCMAKE_INSTALL_PREFIX=<prefix> ..
$ make
$ make install
```

See [CGold guide](https://cgold.readthedocs.io/en/latest/first-step.html) if you need more details on how to build a CMake project.


## Windows/Visual Studio
To compile `drake-lite-cmake` on Windows, it is necessary to use the Clang/LLVM support in Visual Studio,
that needs to be installed as described in Visual Studio official documentation: https://docs.microsoft.com/en-us/cpp/build/clang-support-cmake .
Furthermore, you need to explicitly select it by explicilty specifying as [`CMAKE_GENERATOR_TOOLSET`](https://cmake.org/cmake/help/v3.12/variable/CMAKE_GENERATOR_TOOLSET.html) `ClangCl` , either
using the `-T` CMake command line option or specifying the toolset in the CMake GUI.

Furthermore, at least Visual Studio 16.5 is required. 

### Dependencies
First of all, install all the required dependencies, and make sure that can be found by CMake. 
For the dependencies installed by [vcpkg](https://github.com/microsoft/vcpkg) this tipically happens by passing vcpkg's `CMAKE_TOOLCHAIN_FILE`, 
while for manually installed depedencies you need to add the installation prefix to the [`CMAKE_PREFIX_PATH` enviroment variable](https://cmake.org/cmake/help/latest/variable/CMAKE_PREFIX_PATH.html).

### Compilation
To compile the project from the command line, follow this instructions:
```bash
$ git clone https://github.com/traversaro/drake-lite-cmake
$ cd drake-lite-cmake
$ mkdir build && cd build
$ cmake -T "ClangCl" -DCMAKE_INSTALL_PREFIX=<prefix> ..
$ cmake --build . --target ALL_BUILD --config Release
$ cmake --build . --target INSTALL --config Release
```

Otherwise, see  [CGold guide](https://cgold.readthedocs.io/en/latest/first-step.html) if you need more details on how to build a CMake project.

Note that at the moment the drake headers themself only support be compiled by using the `ClangCl` toolset, so you need to compile any
project that uses drake headers using the `ClangCl` toolset. However, if you have a project that uses drake but that do not expose the drake headers in its
public includes, you can compile it with `ClangCl` and then the library can be used in Visual Studio project that uses other toolsets. 


## Usage
Once the library is installed, you can use it using `CMake` with as little effort as writing the following line of code in your project `CMakeLists.txt`:
```cmake
...
find_package(drake-lite-cmake REQUIRED)
...
target_link_libraries(<target> PRIVATE drake-lite-cmake::drake-lite-cmake)
...
```

# Test the library
`drake-lite-cmake` can run a sample of Drake's tests to make sure that the library is working correctly, to run them just enable the `BUILD_TESTING` CMake option, compile the project and run:
```sh
$ ctest [-VV]
```
to run all the tests.


# API documentation
For API documentation, the users should refer to the official Drake documentation available at https://drake.mit.edu/, at least for the headers and the versions that are distributed with `drake-lite-cmake`.

