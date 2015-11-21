import pickle
import sys

from collections import defaultdict
from copy import copy

def calculateFirst( start, current, direct_first, grammar, ancestors ):
    if current == '$': return
    if current[ 0 ] != '<':
        direct_first[ start ].add( current )

    for rule in grammar[ current ]:
        if rule[ 0 ] not in ancestors:
            calculateFirst( start, rule[ 0 ], direct_first, grammar, ancestors | { current } )

if __name__ == "__main__":
    lines = sys.stdin.readlines()
    lines_iter = iter( lines )

    nonterminals = next( lines_iter ).split()[ 1: ]
    terminals = next( lines_iter ).split()[ 1: ]
    syncs = next( lines_iter ).split()[ 1: ]

    grammar = defaultdict( list )
    all_rules = []
    rules = []
    left_sym = None

    try:
        while True:
            line = next( lines_iter )
            if line[ 0 ] == ' ':
                rules.append( tuple( line.split() ) )
                all_rules.append( ( left_sym, line.split() ) )
            else:
                if left_sym is not None:
                    grammar[ left_sym ] += rules

                left_sym = line.strip()
                rules = []

    except StopIteration:
        grammar[ left_sym ] += rules

    grammar[ '<%>' ] = [ ( nonterminals[ 0 ], ) ]
    nonterminals.insert( 0, '<%>' )

    direct_first = { symbol : set() for symbol in nonterminals }
    empty_symbols = set()

    for symbol, rules in grammar.items():
        for rule in rules:
            if rule[ 0 ] == '$':
                empty_symbols.add( symbol )
                break

    if len( empty_symbols ) > 0: terminals.append( '$' )

    while True:
        new_empty_symbols = copy( empty_symbols )
        for left_sym, rule in all_rules:
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

    for left_sym in nonterminals:
        for rule in grammar[ left_sym ]:
            calculateFirst( left_sym, rule[ 0 ], direct_first, grammar, set() )

    first = copy( direct_first )

    for left_sym, rules in grammar.items():
        for rule in rules:
            for symbol in rule:
                if symbol[ 0 ] == '<':
                    first[ left_sym ] |= direct_first[ symbol ]
                    if symbol not in empty_symbols: break
                else: break

    for symbol in empty_symbols:
        first[ symbol ].add( '$' )

    for term in terminals:
        first[ term ] = { term }


    pickle.dump( {
            'nonterminal'   : nonterminals,
            'terminal'      : terminals,
            'sync'          : syncs,
            'grammar'       : grammar,
            'first'         : first,
            'empty_symbols' : empty_symbols
        }, open( 'analizator/temp_defs.bin', 'wb' ) )
