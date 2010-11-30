#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess, os, sys, optparse, shutil

def get_unify_path():
    relunifypath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
    return os.path.abspath(relunifypath)

sys.path.insert(0, os.path.join(get_unify_path(), "tool", "lib"))

from sassvariants.Precompiler import Precompiler
from sassvariants.Variants import Variants

def which_os(program):
    import os
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def which(program):
    ex = which_os(program)
    if ex != None:
        return ex
    else:
        prog = program + ".exe"
        ex = which_os(prog)
        return ex

def check_inline_sanity(files):
    badfiles = {}
    for file in files:
      count = files.count(file)
      size = os.path.getsize(file) / 1024
      if count > 1 or size > 10:
        badfiles[file] = [count, size]

    for file in badfiles:
      filevals = badfiles[file]
      print("WARNING: %s is inlined %d times and is %.3f kb in size!" % (file, filevals[0], filevals[1]))


def process_variants(sassfile, unifypath, projectresourcepath, oslist):
    variants = Variants(unifypath, projectresourcepath, oslist)
    variants.run(os.path.abspath(sassfile))

    return variants.get_filenames()

def process_precompiler(filenames, unifypath, projectpath, projectresourcepath):
    outfiles = {}
    for variant in filenames:
        inline_files = []
        sassfile = filenames[variant]
        precompiler = Precompiler([projectpath, unifypath])
        precompiler.run(sassfile)
        outfilename = os.path.join(projectresourcepath, "_precompiler." + variant + ".sass")
        precompiler.write_to_file(outfilename)
        outfiles[variant] = outfilename
        check_inline_sanity(precompiler.get_inline_files())

    return outfiles

def process_sass(filename, variant, unifypath, projectresourcepath):
    unifypath = os.path.join(unifypath, "tool", "unify-sass")
    
    jarpath = os.path.normpath(os.path.join(unifypath, "sasscss.jar"))
    unifysasspath = os.path.normpath(os.path.join(unifypath, "unify-sass.rb"))
    sourcepath = filename
    targetpath = os.path.join(projectresourcepath, "style." + variant + ".css")
    
    ruby_exec = which("ruby")
    if ruby_exec != None:
        arg = [ruby_exec, unifysasspath, sourcepath, targetpath]
    else:
        arg = ["java", "-Xms512M", "-Xmx512M", "-jar", jarpath, "-X-C", unifysasspath, sourcepath, targetpath]

    print("Processing " + filename + " with sass compiler")

    subprocess.call(arg, cwd=unifypath)

def main():
    projectpath = os.path.abspath(os.getcwd())
    projectresourcepath = os.path.abspath(os.path.dirname(sys.argv[1]))
    unifypath = get_unify_path()
  
    infile = sys.argv[1]+".sass"

    oslist = ["iphoneos","android"]
 
    filenames = process_variants(sys.argv[1] + ".sass", unifypath, projectresourcepath, oslist)
    filenames = process_precompiler(filenames, unifypath, projectpath, projectresourcepath)

    for variant in filenames:
        filename = filenames[variant]
        process_sass(filename, variant, unifypath, projectresourcepath)

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print()
        print("Keyboard interrupt!")
        sys.exit(1)
