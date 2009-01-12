from helper import normalizeScript

NAMELESS_NODES = ['attribute', 'handler', 'method', 'class']
TAG_NAME_REMAP = {'import':'_import', 'class':'BaseClass'}
NON_COPIED_ATTRS = ['name', 'id', 'extends']

class ClassFactory:
    """ I take a class definition and return a list that when 
        joined is the actual code to make the python class 
    """
    
    def __init__(self, elem):
        self.elem = elem
        
        #if the element has a reserved class name (like "class") we 
        #use a lookup to rewrite it to something usuable (e.g. "class"->"BaseClass")
        if elem.get('name') in TAG_NAME_REMAP: 
            elem.set('name', TAG_NAME_REMAP[elem.get('name')])
        
        #find all import tags and strip thir
        self.imports = [node.get('name') for node in elem.getchildren() if node.tag == 'import']
        
        #find all toplevel methods and create "static methods"
        annotateNamespace = False
        if self.elem.get('extends') != 'none':
            annotateNamespace = True
            
        self.methods = [MethodFactory(node, annotateNamespace=annotateNamespace) for node in elem.getchildren() if node.tag == 'method']

    def flatten(self):
        output = ["","","#CLASS %s" % self.elem.get('name')]
        
        #IMPORTS
        [output.append(imp) for imp in self.imports]
        
        #CLASS INIT
        extends = self.elem.get('extends') or 'node'
        if extends != 'none':
            output.append("class %s(%s):"%(self.elem.get('name'), extends))
        else:
            output.append("class %s:"%(self.elem.get('name')))
            
        #CLASS DEFAULT ATTRIBUTES
        #[output.append("    %s = %s" % (elem.get('name'), AttributeFactory(elem).flatten() ) ) for elem in self.elem.getchildren() if elem.tag == 'attribute']
        [output.extend(AttributeFactory(elem).flatten() ) for elem in self.elem.getchildren() if elem.tag == 'attribute']
        
        
        #if extends != 'none':
        #    #INIT STATEMENT
        #    output.append("    def __init__(self, %s):" %(self.elem.get('args')  or ''))
        #    #calling the parents __init__ if it extends from something
        #    output.append("        %s.__init__(self)" % extends)
        #   output.append("        self.__construct__()")
        #   output.append("        self.__objectgraph__()")
            
        #"STATIC" CLASS METHODS
        for method in self.methods:
            [output.append("    %s"%(line)) for line in method.flatten()]
                
        #OBJECT GRAPH
        output.append("    def __objectgraph__(self, %s):" %(self.elem.get('args')  or ''))
        for child in self.elem.getchildren():
            [output.append("        %s"%o) for o in ObjectGraph(child).flatten()]
        
        #return the list of lines that define this class.
        return output
        
class MethodFactory:
    def __init__(self, elem, annotateNamespace=False):
        self.elem = elem
        self.annotateNamespace = annotateNamespace
        
    def flatten(self):
        buf = ["", "def %s(self, %s):"%(self.elem.get('name'), self.elem.get('args') or '')]
        
        if self.annotateNamespace:
        	buf.append("    parent, application = self.parent, self.application")
               
        [buf.append('    %s' % line) for line in normalizeScript(self.elem.text or '').split('\n')]
        return buf
        
class AttributeFactory:
    types = {'expression':'', 'number':'float', 'string':'str'}
    
    def __init__(self, elem):
        self.elem = elem
        self.name = self.elem.get('name')
        self.type = self.elem.get('type')
        self.value = self.elem.get('value')
        print "!",self.name, self.type, self.value

    def flatten(self):
        #tests for existence and the value of None
        buf = ["","     #attribute: %s" % self.name]

        #buf.append("    if not self['%s']: self['%s'] = type(%s)(%s)" % (self.name, self.name, self.typeof, `self.value`) )

        
        if self.type == 'expression':
            buf.append("     self[%s] = eval(%s,self.parent.__dict__)" % ( self.name, self.value ))
        
        
        #buf.append("    else: ")
        #buf.append("    if %s is not None:" % self.value)
        #buf.append("                     self['%s'] = %s(self['%s'])"%(self.name, self.typeof, self.name) )
        #buf.append("    else: self['%s'] = None" % self.name)

        return buf
        
        
class ObjectGraph:
    """ I take a DOM tree and produce a list python code to instantiate 
        both named and unnamed nodes in a classes' init method
    """
        
    def __init__(self, elem, path=['self']):
        self.elem = elem
        self.path = path
        
    def flatten(self):
        """ I return a list of code lines meant to be added to a classes init method """
        self.lines = []
        self.walk(self.elem, path=self.path, topmostnode=True)
        return ['pass']+self.lines
        
        
    def walk(self, elem, path, topmostnode=False):
        """ I traverse a dom tree in document order, creating python commands
            that would create the same tree - an xml->python object graph creator
        """
        unnamedCounter = 0
                
        #if the encountered tags are either a class definition or an import
        #ignore them, because these are not part of the object graph
        if ['class', 'import'].count(elem.tag): 
            return
            
        #if we are at the top of the object graph - aka - directly under
        #the class defintion, don't process method tags. These are automatically
        #defined as "static methods" and handled in the class factory
        if topmostnode and elem.tag == "method": 
            return
        
        #get the class name
        classname = elem.tag
        
        #get the text of the node, if any
        if elem.text and elem.text.strip():
          elem.attrib['text'] = elem.text            
        else:
          elem.attrib['text'] = ""

        #assign a name if one has not been provided.
        name = elem.get('name')
        if (not name) or elem.tag in NAMELESS_NODES:
          name = "%s_%s_anon"%(classname, unnamedCounter)
          unnamedCounter += 1
          
        #Get the context of the call (o)
        realPath = '.'.join(path)
            
        #make the object creation statement, and continue our little walk in the park
        dot = ''
        if realPath: dot = '.'
        
        self.lines.append("""%s%s%s = %s(%s, %s)"""%(realPath, dot, name, classname, realPath or 'None', `elem.attrib`))
        
        for child in elem.getchildren():
            self.walk(child, path=path+[name])
