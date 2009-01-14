import sys, wildfire

debug = False
try:
    sys.argv[2]
    debug = True
except IndexError: pass
    
try:
    wildfire.load(sys.argv[1],debug=debug)
except IndexError:
    print "You really should pass me a file..."

