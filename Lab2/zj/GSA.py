import sys

from collections import defaultdict

if __name__ == "__main__":
    lines = sys.stdin.readlines()
    lines_iter = iter( lines )

    nonterminal = next( lines_iter ).split()[ 1: ]
    terminal = next( lines_iter ).split()[ 1: ]
    sync = next( lines_iter ).split()[ 1: ]

    print( nonterminal, terminal, sync )

    grammar = defaultdict( list )
    rules = []
    left_sym = None

    try:
        while True:
            line = next( lines_iter )
            if line[ 0 ] == ' ':
                rules.append( tuple( line.split() ) )
            else:
                if left_sym is not None:
                    grammar[ left_sym ] += rules

                left_sym = line.strip()
                rules = []

    except StopIteration:
        grammar[ left_sym ] += rules

    grammar[ '<%>' ] = [ ( nonterminal[ 0 ] ) ]
    nonterminal.insert( 0, '<%>' )

    print( grammar )
