import sys

from definitions import *
from units import *

def preprocess_line( line ):
    if line[ 0 ] == '<':
        return UnitLine( line )
    else:
        return TokenLine( *( line.split() ) )

tlines = sys.stdin.readlines()
lines = [ t.rstrip() for t in tlines ]
indented = [ ( len( line ) - len( line.lstrip() ), preprocess_line( line.lstrip() ) ) for line in lines ]
stack = []
global_scope = Scope()
scope = global_scope
for depth, item in indented:
    while stack and stack[ -1 ].depth >= depth:
        top = stack.pop()
        top.process()
        stack[ -1 ].append( top )
    if isinstance( item, TokenLine ):
        stack[ -1 ].append( Token( item, depth ) )
    else:
        if stack: scope = stack[ -1 ].scope
        print( depth, scope )
        unit = ( get_unit( item.name ) )( depth, scope )
        stack.append( unit )

while len( stack ) > 1:
    top = stack.pop()
    top.process()
    stack[ -1 ].append( top )

stack[ 0 ].process()
print( global_scope )
