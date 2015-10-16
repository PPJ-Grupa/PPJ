import pickle
import sys

def preprocess_regex( regex_str, regexes ):
    temp_regex_str = []
    slash_precedeed = False
    char_replacements = { '{' : '{{', '}' : '}}', '_' : ' ' }

    for char in regex_str:
        if slash_precedeed and char in char_replacements:
            temp_regex_str.append( char_replacements[ char ] )
            slash_precedeed = False
        else:
            temp_regex_str.append( char )
            slash_precedeed = not slash_precedeed if char == '\\' else False

    temp_regex_str = ''.join( temp_regex_str )
    return '(' + temp_regex_str.format( **regexes ) + ')'


if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    regex_defs = [ line for line in lines if line and line[ 0 ] == '{' and len( line ) > 1 ]
    states_list = [ line[ 2: ] for line in lines if line[ :2 ] == '%X' ][ 0 ].split()
    lexemes_list = [ line[ 2: ] for line in lines if line[ :2 ] == '%L' ][ 0 ].split()

    regexes = {}

    for regex_def in regex_defs:
        temp_name, def_str = regex_def.split()
        name = temp_name[ 1:-1 ]
        regexes[ name ] = preprocess_regex( def_str, regexes )

    main_lines = lines[ len( regex_defs ) + 2 : ]

    current_transition = None
    line_count = 0
    transitions = { name : [] for name in states_list }

    for line in main_lines:
        if line:
            if line[ 0 ] == '<':
                state_name, regex = line[ 1: ].split( '>', maxsplit = 1 )
                current_transition = { 'name' : state_name, 'regex' : preprocess_regex( regex, regexes ), 'newline' : False, 'new_state' : state_name }
                line_count = 0
            elif line_count == 2:
                current_transition[ 'lexeme' ] = line.strip() if line[ 0 ] != '-' else None
            elif line.startswith( 'NOVI_REDAK' ):
                current_transition[ 'newline' ] = True
            elif line.startswith( 'UDJI_U_STANJE' ):
                current_transition[ 'new_state' ] = line[ 14: ]
            elif line.startswith( 'VRATI_SE' ):
                current_transition[ 'return_to' ] = int( line[ 8: ] )
            elif line[ 0 ] == '}':
                transitions[ current_transition[ 'name' ] ].append({
                    'regex' : current_transition[ 'regex' ],
                    'lexeme' : current_transition[ 'lexeme' ],
                    'newline' : current_transition[ 'newline' ],
                    'new_state' : current_transition[ 'new_state' ],
                    'return_to' : current_transition.get( 'return_to' ) })
            else: pass

            line_count += 1

    definitions = { 'start_state' : states_list[ 0 ], 'transitions' : transitions }

    pickle.dump( definitions, open( 'temporary_definitions.bin', 'wb' ) )
