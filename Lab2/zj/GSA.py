import pickle
import sys

from collections import defaultdict
from copy import copy
from pprint import pprint


# Global variables
grammar         = defaultdict( list )
rules           = []
empty_symbols   = set()
nonterminals    = []
terminals       = []
symbols         = []
syncs           = []
starts_with     = {}
starts_with_term     = {}
directly_starts_with = {}

nodes           = []
item_node       = {}
node_count      = 0
edge_count      = 0

class Item:
    def __init__( self, rule, pos, lookaheads ):
        self.rule = rule
        self.pos = pos
        self.lookaheads = lookaheads

    def __str__( self ):
        return '{}::{}::{}'.format( self.rule, self.pos, ':'.join( sorted( self.lookaheads ) ) )

    def __repr__( self ):
        rule = rules[ self.rule ]
        return '{} -> {} * {}, {{ {} }}'.format( rule[ 0 ], ' '.join( rule[ 1 ][ :self.pos ] ), ' '.join( rule[ 1 ][ self.pos: ] ), ', '.join( self.lookaheads ) )

    def __hash__( self ):
        return hash( str( self ) )

    def __eq__( self, other ):
        return self.rule == other.rule and self.pos == other.pos and self.lookaheads == other.lookaheads

    @classmethod
    def get_node( cls, item ):
        global item_node
        if item in item_node.keys():
            return item_node[ item ]

        nnode = Node.new_node( item )
        item_node[ item ] = nnode
        return nnode


class Node:
    def __init__( self, item, num ):
        self.num = num
        self.item = item
        self.moves = defaultdict( set )
        self.visited = False

    def add_link( self, node_num, symbol ):
        global edge_count
        edge_count += 1
        self.moves[ symbol ].add( node_num )

    def __str__( self ):
        return '{} :: {}'.format( self.num, repr( self.item ) )

    @classmethod
    def new_node( cls, item ):
        global nodes
        global item_node
        global node_count
        nodes.append( cls( item, node_count ) )
        item_node[ item ] = node_count
        node_count += 1
        return node_count - 1


# Calculate epsilon surrounding of a set of nodes
def epsilon_surround( node_set ):
    surround = copy( node_set )

    for node in node_set:



# Returns a set of all the symbols a given sequence can start with
def sequence_starts_with( sequence ):
    global empty_symbols
    global starts_with_term
    result = set()
    for symbol in sequence:
        result |= starts_with_term[ symbol ]
        if symbol not in empty_symbols: break
    return result

# Test whether a sequence can be transformed into an empty string
def is_empty_seq( sequence ):
    global empty_symbols
    return len( [ symbol for symbol in sequence if symbol not in empty_symbols ] ) == 0


# Get lookaheads
def get_lookaheads( sequence, empty_addition ):
    lookaheads = sequence_starts_with( sequence )
    if is_empty_seq( sequence ):
        lookaheads |= empty_addition
    return lookaheads


# As the name says, main program
if __name__ == "__main__":
    lines = sys.stdin.readlines()
    lines_iter = iter( lines )

    nonterminals    = next( lines_iter ).split()[ 1: ]
    terminals       = next( lines_iter ).split()[ 1: ]
    syncs           = next( lines_iter ).split()[ 1: ]

    left_sym        = None
    rule_count      = 1

    grammar[ '<%>' ] = [ 0 ]
    rules = [ ( '<%>', [ nonterminals[ 0 ] ] ) ]
    nonterminals.insert( 0, '<%>' )
    symbols = nonterminals + terminals

    for line in lines[ 3: ]:
        if line[ 0 ] == ' ':
            grammar[ left_sym ].append( rule_count )
            rules.append( ( left_sym, line.split() ) )
            rule_count += 1
        else:
            left_sym = line.strip()

    directly_starts_with = { symbol : { symbol } for symbol in symbols }

    for left, right in rules:
        if right[ 0 ] == '$':
            empty_symbols.add( left )

    while True:
        new_empty_symbols = copy( empty_symbols )
        for left_sym, rule in rules:
            is_empty = True
            for symbol in rule:
                if symbol not in empty_symbols:
                    is_empty = False
                    break
            if is_empty:
                new_empty_symbols.add( left_sym )
        if len( new_empty_symbols ) == len( empty_symbols ):
            break
        empty_symbols = new_empty_symbols

    for left, right in rules:
        if right[ 0 ] != '$':
            for symbol in right:
                directly_starts_with[ left ].add( symbol )
                if symbol not in empty_symbols: break

    starts_with = copy( directly_starts_with )

    for sym1 in symbols:
        for sym2 in symbols:
            if sym2 in starts_with[ sym1 ]:
                starts_with[ sym1 ] |= starts_with[ sym2 ]

    starts_with_term = { symbol : { x for x in starts_with[ symbol ] if x[ 0 ] != '<' } for symbol in symbols }

    start_item = Item( 0, 0, { '#' } )
    Node.new_node( start_item )

    stack = [ 0 ]
    while stack:
        current = nodes[ stack[ -1 ] ]
        stack.pop()
        if current.visited: continue
        current.visited = True

        citem = current.item
        if citem.pos != len( rules[ citem.rule ][ 1 ] ):
            right_sym = rules[ citem.rule ][ 1 ][ citem.pos ]
            if right_sym == '$': continue
            remains = rules[ citem.rule ][ 1 ][ citem.pos+1: ]
            lookaheads = get_lookaheads( remains, citem.lookaheads )

            # First move one step
            nnode = Item.get_node( Item( citem.rule, citem.pos + 1, citem.lookaheads ) )
            current.add_link( nnode, right_sym )
            if not nodes[ nnode ].visited:
                stack.append( nnode )

            # Then try all epsilons
            for rule_num in grammar[ right_sym ]:
                nnode = Item.get_node( Item( rule_num, 0, lookaheads ) )
                current.add_link( nnode, '$' )
                if not nodes[ nnode ].visited:
                    stack.append( nnode )

    print( node_count )
    print( edge_count )

    for node in nodes:
