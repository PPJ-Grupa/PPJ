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
directly_starts_with = {}

# Calculates a closure of an item set
def closure( item_set ):
    while( True ):
        new_set = copy( item_set )
        for item in item_set:
            num, pos, lookahead = item
            rule = rules[ num ][ 1 ]
            if pos >= len( rule ) or rule[ pos ][ 0 ] != '<': continue
            # print( rule_num, position, own_rule, symbol )
            for index in grammar[ rule[ pos ] ]:
                new_set.add( ( index, 0, 'x' ) )
        if len( item_set ) == len( new_set ): break
        item_set = new_set
    return item_set

# Returns a set of all the symbols a given sequence can start with
def sequence_starts_with( seq ):
    global empty_symbols
    result = set()
    for symbol in sequence:
        result |= starts_with[ symbol ]
        if symbol not in empty_symbols: break
    return result



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

    pprint( rules )
    # pprint( grammar )

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

    # print( rules_list )

    # for i, rule in enumerate( rules_list ):
    #     lhs, rhs = rule
    #     print( i, lhs, '->', ' '.join( rhs ) )
    #     if rhs[ 0 ] != '$':
    #         for j in range( 1, len( rhs ) ):
    #             print( i, j )

    start_item = ( 0, 0, '#' )
    print( start_item )
    print( closure( { start_item } ) )
