#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, sys, optparse, shutil

def get_immediate_subdirs(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

def run_sass(osname,resourcepath,unifypath,basepath):
    print "Processing " + osname
    origfilename = str.replace(basepath + "/" + sys.argv[1], ".sass", "")
    outfile = os.path.normpath(origfilename + "." + osname + ".sass")
    genfile = os.path.normpath(origfilename + "." + osname + ".css")
    infile = os.path.normpath(origfilename + ".sass")
    destination = open(outfile, "w")
    destination.write("@import " + resourcepath + "/core.sass\n")
    destination.write("@import " + resourcepath + "/animation.sass\n")
    destination.write("@import " + resourcepath + "/" + osname + "/style.sass\n\n")
    shutil.copyfileobj(open(infile),destination)
    arg = ["python", unifypath + "/sass.py", outfile, genfile]
   
    subprocess.call(arg, cwd=unifypath)


def main():
    basepath = os.getcwd() 
    resourcepath = basepath + "/" + os.path.dirname(sys.argv[0]) + "/../framework/source/resource/unify/mobile"
    resourcepath = os.path.normpath(resourcepath)
    unifypath = os.path.normpath(basepath + "/" + os.path.dirname(sys.argv[0]))

    for path in get_immediate_subdirs(resourcepath):
        run_sass(path,resourcepath,unifypath,basepath)
    sys.exit(0)    

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print
        print "Keyboard interrupt!"
        sys.exit(1)
