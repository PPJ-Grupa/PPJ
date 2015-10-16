import pickle
import sys

from regex import *

# TODO: Unknown errors, doesn't do what it should

def start_from_state( contents, transitions, state ):
    print( '\n\nStart from', state, '\n\n' )
    running = True
    line_number = 1

    lexemes = []
    remains = contents
    matched_length = 0

    while running and remains:
        if remains[ 0 ] == '\n':
            print( 'ENDLINE' )
        possible_transitions = []
        for index, transition in enumerate( transitions[ state ] ):
            matched, remains = transition[ 'parsed_regex' ].match( remains )
            if matched: possible_transitions.append( ( len( matched ), index, matched, remains, transition ) )

        if not possible_transitions:
            print( 'Unmatched' )
            remains = remains[ 1: ]

        else:
            _, _, matched, remains, transition = max( possible_transitions )
            state = transition[ 'new_state' ]

            if transition[ 'return_to' ]: matched, remains = matched[ :transition[ 'return_to' ] ], matched[ transition[ 'return_to' ]: ] + remains
            if transition[ 'lexeme' ]: lexemes.append( ( transition[ 'lexeme' ], line_number, matched ) )
            if transition[ 'newline' ]: line_number += 1

            print( matched, line_number, state, transition[ 'lexeme' ] )

            matched_length += len( matched )

    return matched_length, lexemes

if __name__ == '__main__':
    definitions = pickle.load( open( 'temporary_definitions.bin', 'rb' ) )
    file_name = sys.argv[ 1 ]

    states = definitions[ 'states' ]
    transitions = definitions[ 'transitions' ]

    for key in transitions.keys():
        for index, rule in enumerate( transitions[ key ] ):
            transitions[ key ][ index ][ 'parsed_regex' ] = Regex( transitions[ key ][ index ][ 'regex' ] )

    with open( file_name, 'r' ) as source_file:
        contents = source_file.read()

        results = [ start_from_state( contents, transitions, state ) for state in states ]

        print( results )
        for lexeme, line_number, token in max( results )[ 1 ]:
            print( lexeme, line_number, token )
