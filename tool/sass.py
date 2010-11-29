#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess, os, sys, optparse, shutil

def get_unify_path():
    relunifypath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
    return os.path.abspath(relunifypath)

sys.path.insert(0, os.path.join(get_unify_path(), "tool", "lib"))

from sassvariants.Precompiler import Precompiler

def main():
    projectpath = os.path.abspath(os.getcwd())
    unifypath = get_unify_path()
   
    precompiler = Precompiler([projectpath, unifypath], ["iphoneos", "android"])
    precompiler.run(sys.argv[1]+".sass")
    precompiler.write_to_file(sys.argv[1]+".tmp.sass")

if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print()
        print("Keyboard interrupt!")
        sys.exit(1)
