import sys

from definitions import *
from units import *

def preprocess_line( line ):
    if line[ 0 ] == '<':
        return UnitLine( line )
    else:
        return TokenLine( *( line.split() ) )

sys.stdout = open( 'a.frisc', 'w' )

tlines = sys.stdin.readlines()
lines = [ t.rstrip() for t in tlines ]
indented = [ ( len( line ) - len( line.lstrip() ), preprocess_line( line.lstrip() ) ) for line in lines ]
stack = []

for depth, item in indented:
    while stack and stack[ -1 ].depth >= depth:
        top = stack.pop()
        stack[ -1 ].append( top )
    if isinstance( item, TokenLine ):
        stack[ -1 ].append( Token( depth, item ) )
    else:
        unit = ( get_unit( item.name ) )( depth )
        stack.append( unit )

while len( stack ) > 1:
    top = stack.pop()
    stack[ -1 ].append( top )

# print( stack[ -1 ] )

global_scope = Scope()
FRISC.generate_header()
FRISC.generate_extra_operators()

stack[ -1 ].descend( global_scope )

FRISC.generate_main_call()
FRISC.generate_final_code()
FRISC.output_final_code()
