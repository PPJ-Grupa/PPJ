import sys
import pickle

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
        if action is None:
            raise ParsingError( 'No action allowed :: {}, {} [{}]'.format( state, symbol, stack[ -2 ] if len( stack ) > 1 else stack )  )
        elif action[ 0 ] == 'R':
            rule = rules[ action[ 1 ] ]
            n = 0 if rule[ 1 ][ 0 ] == '$' else len( rule[ 1 ] )
            if n != 0:
                old_symbols = stack[-2*n:-1:2]
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
    #print( h )
    if type( h[ 0 ] ) == str:
        print( ' '*i + h[ 0 ] )
        if len( h ) > 1:
            for c in h[ 1 ]:
                pp( c, i+1 )
    else:
        print( ' '*i + ' '.join( h[ 0 ] ) )


if __name__ == '__main__':
    defs = pickle.load( open( 'analizator/tables.bin', 'rb' ) )

    action_table    = defs[ 'action_table' ]
    new_state_table = defs[ 'new_state_table' ]
    syncs           = defs[ 'sync' ]
    rules           = defs[ 'rules' ]

    input_list = [ line.rstrip().split( maxsplit = 2 ) for line in sys.stdin.readlines() ]
    input_list.append( '#' )

    i = 0
    while i < len( input_list ):
        try:
            advance( input_list[ i ] )
            i += 1
        except ParsingError as e:
            print( e )
            try:
                sync_symbol = input_list[ i ]
                while sync_symbol[ 0 ] not in syncs:
                    i += 1
                    sync_symbol = input_list[ i ]
                while action_table[ stack[ -1 ] ][ sync_symbol[ 0 ] ] is None:
                    stack = stack[ :-2 ]
            except:
                print( 'Fatal' )

    pp( stack[ 1 ] )
