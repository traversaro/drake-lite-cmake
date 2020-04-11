#!/usr/bin/env python3
#
# A script to generate to extract the C++ source code corresponding to a set of bazel C++ targets.
# Loosely based on https://github.com/lizan/bazel-cmakelists
#
# Usage:
# $ generate-source-files.py --targets //math //systems/framework
#

import argparse
from os import path
import os
import re
import xml.etree.ElementTree as ET
import subprocess
import sys

EXTERNAL_PATTERN = re.compile("^@(.*)\\/\\/")
SOURCE_EXTENSION = set([".h", ".hpp", ".hh", ".hxx", ".c", ".cc", ".cpp", ".cxx"])

def QueryTargets():
  return ' union '.join(FLAGS.targets)

def Exists(fn):
  try:
    os.stat(fn)
    return True
  except OSError:
    sys.stderr.write("Skipping %s ...\n" % fn)
    return False

def GetBasePath(fn):
  fn = fn.replace('/:', '/')
  fn = fn.replace(':', '/')
  if EXTERNAL_PATTERN.match(fn):
    fn = EXTERNAL_PATTERN.sub("external/\\1/", fn)
  return fn.lstrip('/')

def ConvertGeneratedPath(fn):
  bazel_root = 'bazel-' + FLAGS.project
  genfiles_root = 'bazel-genfiles'
  return path.realpath(path.join(genfiles_root, GetBasePath(fn)))

def ConvertExternalPath(fn):
  bazel_root = 'bazel-' + FLAGS.project
  if EXTERNAL_PATTERN.match(fn):
    return path.join(bazel_root, GetBasePath(fn))
  return path.realpath(GetBasePath(fn))

def run_bazel(args):
  sa = os.getenv("BAZEL_STARTUP_ARGS")
  if sa is not None:
    args = sa.split() + args

  args = ['bazel'] + args
  print(args)
  return subprocess.check_output(args).decode('utf-8')

def ExtractSources():
  query = 'kind("source file", deps(kind("cc_.* rule", deps(kind("cc_.* rule", %s)))))' % QueryTargets()
  sources = []
  for fn in run_bazel(['query', '--noimplicit_deps', query]).splitlines():
    if (not FLAGS.external) and EXTERNAL_PATTERN.match(fn):
      continue
    fn = GetBasePath(fn)
    if path.splitext(fn)[1] in SOURCE_EXTENSION:
      sources.append(fn)
  return [source for source in sources if Exists(source)]

def ExtractGenerated():
  query = 'kind("generated file", deps(kind("cc_.* rule", deps(kind("cc_.* rule", %s)))))' % QueryTargets()
  sources = []
  for fn in run_bazel(['query', '--noimplicit_deps', query]).splitlines():
    fn = ConvertGeneratedPath(fn)
    if path.splitext(fn)[1] in SOURCE_EXTENSION:
      sources.append(fn)
  return [source for source in sources if Exists(source)]

def ExtractIncludes():
  query = 'kind(cc_library, deps(kind("cc_.* rule", %s)))' % QueryTargets()
  includes = []
  xml = run_bazel(['query', '--noimplicit_deps', query, '--output', 'xml'])
  tree = ET.fromstring(xml)
  for e in tree.findall(".//list[@name='includes']/.."):
    prefix = e.attrib['name'].split(':')[0]
    for val in [i.attrib['value'] for i in e.findall("list[@name='includes']/string")] + ["."]:
      geninc = path.realpath(path.join(ConvertGeneratedPath(prefix), val))
      includes.append(geninc)

      inc = path.realpath(path.join(ConvertExternalPath(prefix), val))
      includes.append(inc)

  for e in tree.findall(".//string[@name='include_prefix']/.."):
    prefix = e.attrib['name'].split(':')[0]
    include_prefix = e.find("string[@name='include_prefix']").attrib['value']
    geninc = path.realpath(path.join(ConvertGeneratedPath(prefix), val))
    if geninc.endswith(include_prefix):
      geninc = geninc[:-len(include_prefix)]
      includes.append(geninc)
    inc = path.realpath(path.join(ConvertExternalPath(prefix), val))
    if inc.endswith(include_prefix):
      inc = inc[:-len(include_prefix)]
      includes.append(inc)

  for d in os.listdir('bazel-%s/external' % FLAGS.project):
    if os.path.isdir('bazel-%s/external/%s' % (FLAGS.project, d)):
      includes.append(path.realpath('bazel-%s/external/%s' % (FLAGS.project, d)))
    if os.path.isdir('bazel-genfiles/external/%s' % d):
      includes.append(path.realpath('bazel-genfiles/external/%s' % d))

  return set(includes)

def ExtractDefines():
  query = 'attr("defines", "", deps(kind("cc_.* rule", %s)))' % QueryTargets()
  xml = run_bazel(['query', '--noimplicit_deps', query, '--output', 'xml'])
  tree = ET.fromstring(xml)
  defines = []
  for e in tree.findall(".//list[@name='defines']/string"):
    defines.append(e.attrib['value'])
  return set(defines)

def ExtractCopts():
  query = 'attr("copts", "", deps(kind("cc_.* rule", %s)))' % QueryTargets()
  xml = run_bazel(['query', '--noimplicit_deps', query, '--output', 'xml'])
  tree = ET.fromstring(xml)
  copts = []
  for e in tree.findall(".//list[@name='copts']/string"):
    copts.append(e.attrib['value'])
  return set(copts)

def GenerateSourceFilesCMake():
  if FLAGS.build:
    bazel_args = ['build']
    bazel_args.extend(FLAGS.targets)
    bazel_args.extend(FLAGS.bazel_args[1:])
    run_bazel(bazel_args)

  sources = ExtractSources()
  generated = ExtractGenerated()
  includes = ExtractIncludes()
  defines = ExtractDefines()
  copts = ExtractCopts()
  for opt in copts:
    if opt.startswith("-I-"):
      includes.add(opt[3:])
    elif opt.startswith("-I"):
      includes.add(opt[2:])
    elif opt.startswith("-D"):
      defines.add(opt[2:])

  output = FLAGS.output
  file_root = run_bazel(['info', 'workspace']).strip()
  output = path.join(file_root, FLAGS.output)
  try:
    os.remove(output)
  except:
    pass
  with open(output, 'w') as cmakelist:
    cmakelist.write("set(SOURCE_FILES\n    ")
    cmakelist.write("\n    ".join(sources))
    cmakelist.write(")\n\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Generate source_files.cmake that contains the source files of the specified targets.")
  parser.add_argument('--project')
  parser.add_argument('--targets', default=['//...'], nargs='+')
  parser.add_argument('--build', action='store_true', help="Optionally runs the build of the given targetss")
  parser.add_argument('--external', action='store_true', help='Generate project with external')
  parser.add_argument('--output', default="source_files.cmake")
  parser.add_argument('bazel_args', nargs=argparse.REMAINDER)
  FLAGS = parser.parse_args()

  if FLAGS.project is None:
      prj = run_bazel(['info', 'workspace']).strip()
      FLAGS.project = os.path.basename(prj)

  GenerateSourceFilesCMake()
