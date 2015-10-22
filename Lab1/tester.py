#! /usr/bin/env python3
import os
from os.path import isfile, join

cases = { 'tests/integration/' + f.split( '.' )[ 0 ] for f in os.listdir( 'tests/integration' ) if isfile( join( 'tests/integration', f ) ) }
print( cases )
for c in cases:
    os.system( 'python3 generator.py < ' + c + '.lan' )
    os.system( 'python3 analizator.py ' + c + '.in > output.out' )
    os.system( 'cmp ' + c + '.out output.out' )
