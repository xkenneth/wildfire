import sys, wildfire

try:
    wildfire.load(sys.argv[1])
except IndexError:
    print "You really should pass me a file..."

