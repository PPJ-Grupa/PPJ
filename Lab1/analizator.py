import pickle
import sys

from regex import *

# TODO: Unknown errors, doesn't do what it should

if __name__ == '__main__':
    definitions = pickle.load( open( 'temporary_definitions.bin', 'rb' ) )
    file_name = sys.argv[ 1 ]

    state = definitions[ 'start_state' ]
    transitions = definitions[ 'transitions' ]

    for key in transitions.keys():
        for index, rule in enumerate( transitions[ key ] ):
            transitions[ key ][ index ][ 'parsed_regex' ] = Regex( transitions[ key ][ index ][ 'regex' ] )

    with open( file_name, 'r' ) as source_file:
        contents = source_file.read()

        lexemes = []
        line_number = 1

        while contents:
            possible_transitions = []
            for index, transition in enumerate( transitions[ state ] ):
                matched, remains = transition[ 'parsed_regex' ].match( contents )
                if matched:
                    possible_transitions.append( ( len( matched ), -index, matched, remains, transition ) )

            if not possible_transitions:
                print( 'Error at line', line_number, state, '<{}>'.format( contents.split( '\n', maxsplit = 1 )[ 0 ] ), file = sys.stderr )
                contents = contents[ 1: ]
            else:
                _, _, matched, remains, transition = max( possible_transitions )

                if transition[ 'return_to' ]:
                    matched, remains = matched[ :transition[ 'return_to' ] ], matched[ transition[ 'return_to' ]: ] + remains

                if transition[ 'lexeme' ]:
                    lexemes.append( ( transition[ 'lexeme' ], line_number, matched ) )

                if transition[ 'newline' ]:
                    line_number += 1

                state = transition[ 'new_state' ]
                contents = remains

        print( transitions[ 'S_string' ] )

        # for lexeme, line_number, token in lexemes:
        #     print( lexeme, line_number, token )
