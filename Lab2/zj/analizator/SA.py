import sys
import pickle

from TableFromGrammar2 import *

class ParsingError( Exception ):
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return repr( self.value )



action = {}
new_state = {}
stack = [ 0 ]


def advance( symbol ):
    global stack
    state = stack[ -1 ]
    if symbol[ 0 ] in action[ state ]:
        operation, *arg = action[ state ][ symbol[ 0 ] ]
        if operation == 'R':
            pass
        else if operation == 'S':
            pass
        else if operation == 'A':
            return
        else if operation == 'G':
            pass
    else:
        raise ParsingError( 'No transition' )



if __name__ == '__main__':
    defs = pickle.load( open( 'table.bin', 'rb' ) )
    action = defs[ 'action' ]
    new_state = defs[ 'new_state' ]

    # nonterminals    = defs[ 'nonterminal' ]
    # terminals       = defs[ 'terminal' ]
    # syncs           = defs[ 'sync' ]
    # grammar         = defs[ 'grammar' ]
    # first           = defs[ 'first' ]
    # empty_symbols   = defs[ 'empty_symbols' ]
    #
    # table_maker = MakeProductions( nonterminals, terminals, grammar, first, empty_symbols, '<%>' )
    #
    # LRTable = table_maker.make_table()

    input_list = [ line.split( maxsplit = 2 ) for line in sys.stdin.readlines() ]
