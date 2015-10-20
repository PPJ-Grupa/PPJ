#! /usr/bin/env python3

import os
import sys
from os.path import isfile, join

print( 'Starting testing' )
location = 'tests/integration'
cases = { location + '/' + file_name.rsplit( '.', maxsplit = 1 )[ 0 ] for file_name in os.listdir( location ) if isfile( join( location, file_name ) ) }
for case in cases:
    os.system( 'python3 generator.py < ' + case + '.lan' )
    os.system( 'python3 analizator.py ' + case + '.in > output.out 2> /dev/null' )
    c1 = open( 'output.out', 'r' ).read()
    c2 = open( case + '.out', 'r' ).read()
    print( case.ljust( 40 ), '[{}]'.format( 'OK' if c1 == c2 else 'Fail' ) )
