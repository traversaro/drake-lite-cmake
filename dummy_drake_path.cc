#include "drake/common/drake_path.h"

namespace drake {

std::optional<std::string> MaybeGetDrakePath() {
  // As drake-lite-cmake does not install drake's resources, we reimplement 
  // MaybeGetDrakePath to always return an empty std::optional
  // Note that this is necessary only because multibody/parsers depend on this 
  // function to find resourses of URDF and SDF stored inside the drake source 
  // tree, but it is not actually used to load external URDF and SDF 
  return std::nullopt;
}

}  // namespace drake
