#
# SASS Variants Precompiler
#

import re, os, base64

class Variants():
  def __init__(self, unifypath, projectpath, variants):
    self.__unifypath = unifypath
    self.__projectpath = projectpath
    self.__variants = variants

  def run(self, filename):
    content = open(filename, encoding="utf-8").read()
    for variant in self.__variants:
      sassname = self.__get_filename(variant)
      outfile = open(sassname, mode="w", encoding="utf-8")
      outfile.write("@import " + os.path.join(self.__unifypath, "framework/source/resource/unify/mobile", "style." + variant + ".sass") + "\n" + content)

  def __get_filename(self, variant):
    return os.path.join(self.__projectpath, "", "_precompile." + variant + ".sass")

  def get_filenames(self):
    filenames = []
    for variant in self.__variants:
      filenames.append(self.__get_filename(variant))
    return filenames
