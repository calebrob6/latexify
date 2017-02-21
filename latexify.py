#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.

import sys
import os
import subprocess
import random
import argparse
import string

# Mimics the `which` unix command
# Taken from: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def doArgs(argList, name):
    parser = argparse.ArgumentParser(description=name)

    parser.add_argument("-v", "--verbose", action="store_true", help="Show output from latex and dvipng commands", default=False)
    parser.add_argument("expression", type=str, help="Math expression to typeset in latex")
    parser.add_argument("-o", "--outputFn", action="store", dest="outputFn", type=str, help="Output file name (will be a PNG file)", default="temp.png")
    parser.add_argument("-d", "--dpi", action="store", dest="dpi", type=int, help="DPI of output PNG", default=120)
    parser.add_argument("--tempDir", action="store", dest="tempDir", type=str, help="Directory where latex's intermediate files will be written to", default="/tmp")

    return parser.parse_args(argList)

def main():

    if which("latex") == None or which("dvipng") == None:
        print "Error! The commands `latex` and `dvipng` are required and could not be found in your environment."
        return

    args = doArgs(sys.argv[1:], "LaTeX to PNG utility")

    verbose = args.verbose
    expression = args.expression
    outputFn = args.outputFn
    dpi = args.dpi
    tempDir = args.tempDir

    if not outputFn.endswith(".png"):
        outputFn += ".png"

    # Create a random 16 letter filename
    tempFn = "latexify_" + "".join([random.choice(string.ascii_lowercase) for _ in range(16)])
    
    # Record the starting directory, then change to a temporary directory so latex's intermediate files don't make a mess
    startDir = os.getcwd()
    os.chdir(tempDir)

    # Write out a temporary file containing enough latex code to hold the input expression
    # The minimal documentclass type will turn off page numbers 
    f = open("%s.tex" % tempFn, "w")
    f.write("\documentclass{minimal}\n")
    f.write("\\begin{document}\n")
    f.write("$%s$\n" % sys.argv[1])
    f.write("\\end{document}\n")
    f.close()
    
    # If we aren't using verbose mode, direct stdout and stderr from `latex` and `dvipng` to /dev/null
    stdout=None # default setting for stdout and stderr keywords in subprocess.call
    stderr=None
    nullFile = open(os.devnull, 'w')
    if not verbose:
        stdout = nullFile
        stderr = nullFile

    if verbose:
        print "latex output"
        print "-" * 40
        print ""

    # We call `latex` in nonstop mode to generate a .dvi file from our temporary latex file.
    subprocess.call(["latex","-src","-interaction=nonstopmode", "%s.tex" % tempFn], stdout=stdout, stderr=stderr)
    
    # Change back to whatever directory we started from so that our output file will be in the correct place
    os.chdir(startDir)
    
    if verbose:
        print "\n"*2
        print "dvipng output"
        print "-" * 40
        print ""
    
    # We then call `dvipng` to create a cropped png from the dvi output from latex.
    # We also allow the user to change the dpi to get different sized outputs. 
    subprocess.call([
        "dvipng",
        "--width*", "--height*",
        "-T", "tight",
        "-D", "%d" % (dpi),
        "%s.dvi" % (os.path.join(tempDir,tempFn)),
        "-o", outputFn
    ], stdout=stdout, stderr=stderr)

    nullFile.close()

if __name__ == "__main__":
    main()
