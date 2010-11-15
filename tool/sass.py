#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, sys, optparse, shutil

def get_immediate_subdirs(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

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

def run_sass(osname,resourcepath,unifypath,basepath):
    print "Processing " + osname
    origfilename = str.replace(basepath + "/" + sys.argv[1], ".sass", "")
    outfile = os.path.normpath(origfilename + "." + osname + ".sass")
    genfile = os.path.normpath(origfilename + "." + osname + ".css")
    infile = os.path.normpath(origfilename + ".sass")
    destination = open(outfile, "w")
    arg = ["python", unifypath + "/sass.py", outfile, genfile]
   
    subprocess.call(arg, cwd=unifypath)

def copyover(source, osname, resource):
    destination = open(source + "." + osname + ".sass", "w")
    destination.write("@import " + resource + "/core.sass\n")
    destination.write("@import " + resource + "/animation.sass\n")
    destination.write("@import " + resource + "/" + osname + "/style.sass\n\n")
    shutil.copyfileobj(open(source + ".sass", "r"),destination)
    destination.close()


def main():
    basepath = os.getcwd() 
    unifypath = basepath + "/" + os.path.dirname(sys.argv[0]) + "/unify-sass"
    resourcepath = basepath + "/" + os.path.dirname(sys.argv[0]) + "/../framework/source/resource/unify/mobile"
    resourcepath = os.path.normpath(resourcepath)
    
    jarpath = os.path.normpath(unifypath + "/sasscss.jar")
    unifysasspath = os.path.normpath(unifypath + "/unify-sass.rb")
    sourcepath = os.path.normpath(basepath + "/" + sys.argv[1])
    
    ruby_exec = which("ruby")

    for osname in get_immediate_subdirs(resourcepath):
        copyover(sourcepath, osname, resourcepath)
        newsourcepath = sourcepath + "." + osname + ".sass"
        newtargetpath = sourcepath + "." + osname + ".css"
        if ruby_exec != None:
            arg = [ruby_exec, unifysasspath, newsourcepath, newtargetpath]
        else:
            arg = ["java", "-Xms512M", "-Xmx512M", "-jar", jarpath, "-X-C", unifysasspath, newsourcepath, newtargetpath]
  
        print "Processing " + osname + " ..."
 
        subprocess.call(arg, cwd=unifypath)

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print
        print "Keyboard interrupt!"
        sys.exit(1)
