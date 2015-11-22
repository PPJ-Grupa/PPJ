import sys
import pickle

from TableFromGrammar2 import *

class ParsingError( Exception ):
    pass


action_table    = {}
new_state_table = {}
rules           = []
stack           = [ 0 ]


def advance( symbol ):
    global stack
    state = stack[ -1 ]
    if symbol[ 0 ] in action_table[ state ]:
        action = action_table[ state ][ symbol[ 0 ] ]
        print( state, action )
        if action is None: # greska
            raise ParsingError( 'No action allowed' )
        elif action[ 0 ] == 'R':
            rule = rules[ action[ 1 ] ]
            n = 0 if rule[ 1 ][ 0 ] == '$' else len( rule[ 1 ] )
            if n != 0:
                old_symbols = stack[ -2 ]
                stack = stack[ :-2*n ]
            else:
                old_symbols = [ '$' ]

            old_state = stack[ -1 ]
            stack.append( ( rule[ 0 ], old_symbols ) )

            if rule[ 0 ] not in new_state_table[ old_state ]:
                raise ParsingError( 'Unknown new state after reduction' )

            stack.append( new_state_table[ old_state ][ rule[ 0 ] ] )
            advance( symbol )

        elif action[ 0 ] == 'S':
            stack.append( ( symbol, [] ) )
            stack.append( action[ 1 ] )
        elif action[ 0 ] == 'A':
            return
        else:
            pass
    else:
        raise ParsingError( 'No transition' )


def pp( h, i = 0 ):
    print( h )
    #if len( h[ 0 ] ) == 2:
    #    print( " "*i + str( h[ 0 ][ 0 ] ) + " " + str( h[ 0 ][ 1 ] ) )
    #else:
    #     print( " "*i + str( h[ 0 ] ) )
    #if len( h ) < 2: # not sure if best way
    #    return
    #for l in h[ 1 ]:
    #    pp( l, i + 1 )


if __name__ == '__main__':
    defs = pickle.load( open( 'analizator/tables.bin', 'rb' ) )

    action_table    = defs[ 'action_table' ]
    new_state_table = defs[ 'new_state_table' ]
    syncs           = defs[ 'sync' ]
    rules           = defs[ 'rules' ]

    input_list = [ line.split( maxsplit = 2 ) for line in sys.stdin.readlines() ]
    input_list.append( '#' )

    for symbol in input_list:
        try:
            advance( symbol )
        except ParsingError:
            print( 'Error parsing', symbol )
            try:
                sync_symbol = symbol
                while syn_symbol[ 0 ] not in syncs:
                    syn_symbol = next( input_list )
                while syn_symbol[ 0 ] not in action_table[ stack[ -1 ] ]:
                    stack = stack[ :-2 ]
            except StopIteration:
                print( 'Finished parsing with unrecovered error' )
            except IndexError:
                print( 'Could not recover from an error' )

    pp( stack[ 1 ] )
