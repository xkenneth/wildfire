import os
import sys
import xml.etree.ElementTree as et
import wildfire
import traceback

from factory import ObjectGraph

from factory import ClassFactory

appPath = os.path.join(os.getcwd(), 'app.py')
basePath = os.path.join(os.path.split(wildfire.__file__)[0],'base.wfx')

from factory import ClassFactory

def displayError(e,quit=True):
    print "The Wildfire Compiler has encountered an error:"
    print ""
    print ""
    print "Error:"
    print ""
    raise e
    #if quit:
    #    sys.exit()


def loadFile(path):
    f = open(path)
    file_str = f.read()
    
    #!MAKE THIS CODE SEARCH FOR AN EOF RIGHT AFTER A NEWLINE INSTEAD OF ANYWHERE

    if len(file_str.split('EOF')) == 2:
        xml_dom , comments = file_str.split('EOF')
    else:
        xml_dom = file_str
        comments = ""
    
    dom = et.fromstring(xml_dom.strip())
    
    return dom, comments

def load(file, debug=True):
    """Parse the XML file, create the environment, and ....leaving the running up to the libraries!"""
    
    
    print "Loading base tags..."

    try:
        baseDom, comments = loadFile(basePath)
    except Exception, e:
        print "Error loading base classes!"
        displayError(e)

    print "Compiling base classes..."

    try:
        baseClasses = [ClassFactory(elem) for elem in baseDom.getiterator('class')]
    except Exception, e:
        print "Error compiling base classes!"
        displayError(e)

    print "Loading application..." 

    try:
        appDom, comments = loadFile(file)
    except Exception, e:
        print "Error loading application!"
        displayError(e)

    print "Compiling application..."
    
    try:
        appClasses = [ClassFactory(elem) for elem in appDom.getiterator('class')]
    except Exception, e:
        print "Error generating application!"
        displayError(e)

    print "Writing application..."
    
    #try:
    t = open(appPath,'w')
    
        #write the base classes
    [t.write("\n".join(c.flatten())) for c in baseClasses]
    
        #write the app classes
    [t.write("\n".join(c.flatten())) for c in appClasses]
    
        #Make the applications' object graph, and since we don't have self (it runs in the main of the module)
        #set the path to nothin' ([], it would normally be ['self'])
    
    #set the name of the app to be application
    appDom.set('name','application')
    
    #create the application class
    applicationClass = ClassFactory(appDom)

    #write it to the file
    t.write("\n".join(applicationClass.flatten()))
    #applicationObjectGraph = ObjectGraph(appDom, path=[])
    
    #write the "bootloader"
    t.write("\n\nif __name__ == '__main__':\n    application()")
    #t.write("\n    ".join(applicationObjectGraph.flatten()))
    
    t.close()
    
    print "Finished loading. Printing the compiled application:\n"
    #except Exception, e:
    #    print "Error writing application!"
    #    displayError(e)
