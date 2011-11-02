#!/usr/bin/env python3

APPLICATION = "${Namespace}.Application"

QOOXDOOPATH = '${REL_QOOXDOO_PATH}'
UNIFYPATH = QOOXDOOPATH + '/../..'
JASYPATH = UNIFYPATH + "/support/jasy/jasy"

# Extend PYTHONPATH with 'lib'
import sys, os
from time import strftime
sys.path.insert(0, "%s/lib/jasy" % JASYPATH)
sys.path.insert(0, "%s/support/jasy/lib" % UNIFYPATH)

from jasy.Error import *
from jasy.Session import *
from jasy.Project import *
from jasy.Resolver import *
from jasy.Sorter import *
from jasy.Combiner import *
from jasy.Assets import *
from jasy.Optimization import *
from jasy.Format import *
from jasy.File import *
from jasy.Task import *

from unify import Qooxdoo


#
# Tasks
#





#@task
#def simple():
#    # Setup session
#    session = Session()
#    session.addProject(Project("."))
#
#    # Collecting projects
#    resolver = Resolver(session.getProjects())
#    resolver.addClassName("ootest.Test")
#    
#    # Resolving classes
#    classes = Sorter(resolver).getSortedClasses()
#    
#    # Compressing classes
#    compressedCode = Combiner(classes).getCompressedCode()
#    
#    # Writing files
#    writefile("build/simple.js", compressedCode)


def getsession():
    # Setup session
    session = Session()
    
    patcher = Qooxdoo.Patcher(session)
    patcher.patchClasses()
    
    session.addProject(Project("%s/support/jasy/lib/qxpatchjs" % UNIFYPATH))
    session.addProject(Project("%s/unify/framework" % UNIFYPATH, patcher.treePatcher))
    session.addProject(Project("%s/qooxdoo/qooxdoo/framework" % UNIFYPATH, patcher.treePatcher))
    session.addProject(Project(".", patcher.treePatcher), True)
    #session.permutateField("debug")
    #session.permutateField("es5")
    #session.permutateField("engine")
    session.permutateField("locale", ["en"])
    
    session.setField("qx.application", APPLICATION)
    session.setField("qx.debug", "true")
    session.setField("qx.aspects", False)
    
    return session


@task
def clear():
    # Setup session
    session = getsession()

    # Clearing cache
    logging.info("Clearing cache...")
    session.clearCache()
    

@task
def api():
    None
    
    
@task
def source():
    None

@task
def build():
    session = getsession()
    
    # Permutation independend config
    optimization = Optimization() #Optimization("unused", "privates", "variables", "declarations", "blocks")
    #optimization = Optimization("unused", "privates", "variables", "declarations", "blocks")
    formatting = Format("semicolon", "comma")
    #formatting = Format()

    # Store loader script
    loaderIncluded = session.writeLoader("build/loader.js", optimization, formatting)
    
    # Copy HTML file from source
    updatefile("source/index.html", "build/index.html")

    # Process every possible permutation
    permutations = session.getPermutations()
    for pos, permutation in enumerate(permutations):
        logging.info("Permutation %s/%s" % (pos+1, len(permutations)))

        # Get projects
        projects = session.getProjects(permutation)

        # Resolving dependencies
        resolver = Resolver(projects, permutation)
        resolver.addClassName(APPLICATION)
        resolver.excludeClasses(loaderIncluded)
        classes = resolver.getIncludedClasses()

        # Compressing classes
        translation = session.getTranslation(permutation.get("locale"))
        classes = Sorter(resolver, permutation).getSortedClasses()
        compressedCode = Combiner(classes).getCompressedCode(permutation, translation, optimization, formatting)
        
        # Boot logic
        configCode = "window.qx = { $$$$loader : { scriptLoaded: false } };"
        configCode += "window.qx.$$$$build = '%s';" % strftime("%Y-%m-%d %H:%M:%S")
        bootCode = "window.qx.$$$$loader.scriptLoaded = true;"

        # Write file
        writefile("build/${Namespace}-%s.js" % permutation.getChecksum(), configCode + compressedCode + bootCode)

#
# Execute Jasy
#

#run()
if __name__ == "__main__":
    import jasy

    (options, args) = jasy.parseCommandline()
    jasy.runTasks(args)
