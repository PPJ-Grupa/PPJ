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

states          = []
state_nums      = {}
state_count     = 0

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

    def __lt__( self, other ):
        return self.rule < other.rule

    @classmethod
    def get_node( cls, item ):
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
        self.moves[ symbol ].add( node_num )

    def __str__( self ):
        return '{} :: {}'.format( self.num, repr( self.item ) )

    @classmethod
    def new_node( cls, item ):
        global node_count
        nodes.append( cls( item, node_count ) )
        item_node[ item ] = node_count
        node_count += 1
        return node_count - 1


class State:
    def __init__( self, node_set, num = -1 ):
        self.nodes = node_set
        self.num = num
        self.moves = defaultdict( int )
        self.visited = False

    def add_link( self, state, symbol ):
        self.moves[ symbol ] = state

    def __str__( self ):
        return ':'.join( map( str, sorted( self.nodes ) ) )

    def __repr__( self ):
        return '{} :: {{ {} }}'.format( self.num, ', '.join( map( str, sorted( self.nodes ) ) ) )

    def __hash__( self ):
        return hash( str( self ) )

    def __eq__( self, other ):
        return self.nodes == other.nodes

    @classmethod
    def new_state( cls, node_set ):
        global state_count
        state = State( node_set, state_count )
        states.append( state )
        state_nums[ state ] = state_count
        state_count += 1
        return state

    @classmethod
    def get_state( cls, node_set ):
        state = cls( node_set )
        if state in state_nums:
            return state_nums[ state ]

        state = State.new_state( node_set )
        return state.num

# Calculate epsilon surrounding of a set of nodes ( or a list )
def epsilon_surround( node_set ):
    surround = set()
    stack = list( node_set )
    while stack:
        node = stack[ -1 ]
        stack.pop()
        if node in surround: continue
        surround.add( node )
        for adj in nodes[ node ].moves[ '$' ]:
            if adj not in surround:
                stack.append( adj )
    return surround


# Advance a set of nodes by a given move
def advance( node_set, symbol ):
    result = set()
    for node in node_set:
        result |= nodes[ node ].moves[ symbol ]
    return result


# Returns a set of all the symbols a given sequence can start with
def sequence_starts_with( sequence ):
    result = set()
    for symbol in sequence:
        result |= starts_with_term[ symbol ]
        if symbol not in empty_symbols: break
    return result

# Test whether a sequence can be transformed into an empty string
def is_empty_seq( sequence ):
    return len( [ symbol for symbol in sequence if symbol not in empty_symbols ] ) == 0


# Get lookaheads
def get_lookaheads( sequence, empty_addition ):
    lookaheads = sequence_starts_with( sequence )
    if is_empty_seq( sequence ):
        lookaheads |= empty_addition
    return lookaheads


# Helper function, tests whether a given item is an end position in a rule
def is_end_position( item ):
    return rules[ item.rule ][ 1 ][ item.pos ] == '$' if item.pos < len( rules[ item.rule ][ 1 ] ) else True


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
    symbols = [ '<%>' ] + nonterminals + terminals

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

    start_set = epsilon_surround( { 0 } )

    # eNKA to NKA conversion, very slow for PPJLang, 19sec
    for node in nodes:
        surround = epsilon_surround( { node.num } )
        for symbol in symbols:
            node.moves[ symbol ] |= epsilon_surround( advance( surround, symbol ) )

    # NKA to DKA conversion
    start_state = State.get_state( start_set )
    stack = [ start_state ]
    while stack:
        state = states[ stack[ -1 ] ]
        stack.pop()
        if state.visited: continue
        state.visited = True

        for symbol in symbols:

            next_set = set()
            for node in state.nodes:
                next_set |= nodes[ node ].moves[ symbol ]

            if len( next_set ) == 0: continue
            nstate = State.get_state( next_set )
            state.add_link( nstate, symbol )
            if not states[ nstate ].visited:
                stack.append( nstate )

    new_state_table = [ dict.fromkeys( nonterminals ) for _ in range( state_count ) ]
    action_table = [ dict.fromkeys( terminals + [ '#' ] ) for _ in range( state_count ) ]

    for state in states:
        # Fill in new_state_table
        for symbol in nonterminals:
            if symbol in state.moves:
                new_state_table[ state.num ][ symbol ] = state.moves[ symbol ]

        # Set accept action, if there
        if 1 in state.nodes:
            action_table[ state.num ][ '#' ] = ( 'A', )

        local_items = sorted( [ nodes[ node ].item for node in state.nodes ] )

        # Set shift actions
        for item in local_items:
            if item.pos != len( rules[ item.rule ][ 1 ] ):
                symbol = rules[ item.rule ][ 1 ][ item.pos ]
                if symbol in nonterminals or symbol == '$': continue
                if symbol in state.moves:
                    if action_table[ state.num ][ symbol ] is None:
                        action_table[ state.num ][ symbol ] = ( 'S', state.moves[ symbol ] )

        # Set reduce actions
        for item in local_items:
            if is_end_position( item ):
                for symbol in item.lookaheads:
                    if action_table[ state.num ][ symbol ] is None:
                        action_table[ state.num ][ symbol ] = ( 'R', item.rule )

    cterminals = terminals + [ '#' ]
    print( ' '.ljust( 5 ), end = '' )
    for sym in cterminals:
        print( sym.ljust( 12 ), end = '' )
    for state in states:
        print( '' )
        print( str( state.num ).ljust( 5 ), end = '' )
        for sym in cterminals:
            print( str( action_table[ state.num ][ sym ] ).ljust( 12 ), end = '' )
    print()

    # print( new_state_table )

    pickle.dump( {
        'nonterminals' : nonterminals,
        'terminals' : terminals,
        'sync' : syncs,
        'rules' : rules,
        'new_state_table' : new_state_table,
        'action_table' : action_table
    }, open( 'analizator/tables.bin', 'wb' ) )
