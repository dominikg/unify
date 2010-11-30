#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess, os, sys, optparse, shutil

def get_unify_path():
    relunifypath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
    return os.path.abspath(relunifypath)

sys.path.insert(0, os.path.join(get_unify_path(), "tool", "lib"))

from sassvariants.Precompiler import Precompiler
from sassvariants.Variants import Variants

def process_variants(sassfile, unifypath, projectresourcepath, oslist):
    variants = Variants(unifypath, projectresourcepath, oslist)
    variants.run(os.path.abspath(sassfile))

    return variants.get_filenames()

def process_precompiler(filenames, unifypath, projectpath, projectresourcepath):
    outfiles = {}
    for variant in filenames:
        sassfile = filenames[variant]
        print(variant, sassfile)
        precompiler = Precompiler([projectpath, unifypath])
        precompiler.run(sassfile)
        outfilename = os.path.join(projectresourcepath, "_precompiler." + variant + ".sass")
        precompiler.write_to_file(outfilename)
        outfiles[variant] = outfilename

    return outfiles

def main():
    projectpath = os.path.abspath(os.getcwd())
    projectresourcepath = os.path.abspath(os.path.dirname(sys.argv[1]))
    unifypath = get_unify_path()
  
    infile = sys.argv[1]+".sass"

    oslist = ["iphoneos","android"]
 
    filenames = process_variants(sys.argv[1] + ".sass", unifypath, projectresourcepath, oslist)
    filenames = process_precompiler(filenames, unifypath, projectpath, projectresourcepath)

    print("Files created: ", filenames)

    #precompiler = Precompiler([projectpath, unifypath], oslist)
    #precompiler.run(infile)
    #precompiler.write_to_file(sys.argv[1])

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print()
        print("Keyboard interrupt!")
        sys.exit(1)
