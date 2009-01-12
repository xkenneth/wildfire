#
# Python
#
import re

#
# Module
#
from xml.etree.ElementTree import fromstring, tostring



space_re = re.compile('\s*')
tab_re = re.compile('t*')
constraint_re = re.compile('\${.*}')

#
# COUNTER
#

counter = 0

def nextCount():
    """Return the next iteration in an incrementing count."""
    global counter
    counter += 1
    return counter

#
# CLONE
#
def clone(element):
    """Clone an element node."""
    return fromstring(tostring(element))
    
# 
# HANDLERS
#

def call_handlers(node):
    """Call handlers in the proper order."""
    do(node,'construct')
    do(node,'init')
    do_post(node,'script')
    do_post(node,'late')
    
def do(node,attr):
    """Fire handlers with a pre-order traversal."""
    node[attr] = True
    for sub_node in node.childNodes:
        do(sub_node,attr)

def do_post(node,attr):
    """Fire handlers with a post-order traversal."""

    for sub_node in node.childNodes:
        do_post(sub_node,attr)

    node[attr] = True

#
# EXTENSION
#
def extend(target,source,nodes=True,attributes=True,ignore_duplicates=False):
    """Extend a class with another."""

    #create copies of the nodes
    target = clone(target)
    source = clone(source)
    
    #for all the child nodes in the source, append them to the target
    if nodes:
        for i in source:
            target.append(i)

    #if we want the attributes
    if attributes:
        #for all of the attributes in the source
        for new_attr in source.keys():
            #if it's not a reserved keyword
            if not new_attr in source.KEYATTRS:
                #add them to the target
                target.set(new_attr,source.get(new_attr))
                
    return target
    
#
# CONSTRAINTS
#

def is_constraint(str):
    """Test whether or not a string matches the constraint syntax."""
    match = constraint_re.match(str)
    if match:
        #if we've got a group, slice and return
        return True
    else:
        return False
        
        
def normalizeScript(script):
    #make sure that it has any newlines in the first place..
    #! THIS PROBABLY SHOULD SET THE LINE TO ZERO INDENT IN THIS CASE - james
    if script.find('\n') == -1:
        return script

    #split by line, take the first empty line out
    lines = script.split('\n')

    #get rid of the first line if it's empty
    while lines[0].strip() == '':
        lines = lines[1:]

    #find out the number of tabs at the front of the line
    num_spaces = len(space_re.match(lines[0]).group())

    proper_script = ''
    #for each line, remove the number of tabs
    for line in lines:
        proper_script += line[num_spaces:] + '\n'

    return proper_script


def normalizeScript(value):
    """
        This analyzes a piece of python script to derive the proper first
        indent (by looking at the first line) and adjusts the rest accordingly.
        Pass either a dom or a string, with an _unindented_ prefix and then 
        definition line that wraps the code for later execution into a namespace.
    """
    value = value.split('\n')
    
    #find indent
    for line in value:
      if not line.strip(): 
          continue
      else: 
          indent = len(line) - len(line.lstrip())
          break
    
    script = []
    
    #normalize script tab depth to zero, reindenting if wrapped in a defintion
    for line in value:
      strippedline = line.strip()
      if not strippedline or strippedline[0] == '#': continue
      script.append(line[indent:])
      
    return '\n'.join(script)
