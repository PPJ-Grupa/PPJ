import sys
import pickle

from TableFromGrammar2 import *

class ParsingError( Exception ):
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return repr( self.value )

if __name__ == '__main__':
    defs = pickle.load( open( 'temp_defs.bin', 'rb' ) )

    nonterminals    = defs[ 'nonterminal' ]
    terminals       = defs[ 'terminal' ]
    syncs           = defs[ 'sync' ]
    grammar         = defs[ 'grammar' ]
    first           = defs[ 'first' ]
    empty_symbols   = defs[ 'empty_symbols' ]

    table_maker = MakeProductions( nonterminals, terminals, grammar, first, empty_symbols, '<%>' )

    LRTable = table_maker.make_table()

    
