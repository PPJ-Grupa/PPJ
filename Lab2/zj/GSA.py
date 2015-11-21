import pickle
import sys

from collections import defaultdict
from copy import copy

# def calculateFirst( start, current, direct_first, grammar, ancestors ):
#     if current == '$': return
#     if current[ 0 ] != '<':
#         direct_first[ start ].add( current )
#
#     for rule in grammar[ current ]:
#         if rule[ 0 ] not in ancestors:
#             calculateFirst( start, rule[ 0 ], direct_first, grammar, ancestors | { current } )

def sequence_starts_with( seq, starts_with, empty_symbols ):
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

    grammar     = defaultdict( list )
    rules_list  = []
    rules       = []
    left_sym    = None

    try:
        while True:
            line = next( lines_iter )
            if line[ 0 ] == ' ':
                rules.append( line.split() )
                rules_list.append( ( left_sym, line.split() ) )
            else:
                if left_sym is not None:
                    grammar[ left_sym ] += rules

                left_sym = line.strip()
                rules = []

    except StopIteration:
        grammar[ left_sym ] += rules

    grammar[ '<%>' ] = [ [ nonterminals[ 0 ] ] ]
    rules_list.append( ( '<%>', [ nonterminals[ 0 ] ] ) )
    nonterminals.insert( 0, '<%>' )
    symbols = nonterminals + terminals

    directly_starts_with = { symbol : { symbol } for symbol in symbols }
    empty_symbols = set()

    for left, right in rules_list:
        if right[ 0 ] == '$':
            empty_symbols.add( left )

    # if len( empty_symbols ) > 0: terminals.append( '$' )

    # print( all_rules )

    while True:
        new_empty_symbols = copy( empty_symbols )
        for left_sym, rule in rules_list:
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

    print( empty_symbols )

    for left, right in rules_list:
        if right[ 0 ] != '$':
            for symbol in right:
                directly_starts_with[ left ].add( symbol )
                if symbol not in empty_symbols: break

    print( directly_starts_with )

    starts_with = copy( directly_starts_with )

    for sym1 in symbols:
        for sym2 in symbols:
            if sym2 in starts_with[ sym1 ]:
                starts_with[ sym1 ] |= starts_with[ sym2 ]

    print( starts_with )



    # for left_sym in nonterminals:
    #     for rule in grammar[ left_sym ]:
    #         calculateFirst( left_sym, rule[ 0 ], direct_first, grammar, set() )
    #
    # first = copy( direct_first )
    #
    # for left_sym, rules in grammar.items():
    #     for rule in rules:
    #         for symbol in rule:
    #             if symbol[ 0 ] == '<':
    #                 first[ left_sym ] |= direct_first[ symbol ]
    #                 if symbol not in empty_symbols: break
    #             else: break
    #
    # for symbol in empty_symbols:
    #     first[ symbol ].add( '$' )
    #
    # for term in terminals:
    #     first[ term ] = { term }
    #
    # print( direct_first )
    # print( first )

    # pickle.dump( {
    #         'nonterminal'   : nonterminals,
    #         'terminal'      : terminals,
    #         'sync'          : syncs,
    #         'grammar'       : grammar,
    #         'first'         : first,
    #         'empty_symbols' : empty_symbols
    #     }, open( 'analizator/temp_defs.bin', 'wb' ) )
