#
# SASS Variants Precompiler
# 
#  Part of the unify project
#  License: MIT + Apache (V2)
#  Homepage: unify-training.com
#  Copyright: 2010 Sebastian Fastner, Mainz, http://www.sebastianfastner.de
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

      vcontent = "@import " + os.path.join(self.__projectpath, "style." + variant + ".sass") + "\n"
      vcontent += "@import " + os.path.join(self.__unifypath, "framework/source/resource/unify/mobile", "style." + variant + ".sass") + "\n"
      vcontent += content

      outfile.write(vcontent)

  def __get_filename(self, variant):
    return os.path.join(self.__projectpath, "", "_variant." + variant + ".sass")

  def get_filenames(self):
    filenames = {}
    for variant in self.__variants:
      filenames[variant] = self.__get_filename(variant)
    return filenames
