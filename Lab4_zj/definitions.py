################################################################################
# Utilities                                                              #
################################################################################

class FRISC:
    """Helper class having only static methods dealing with properties of resulting FRISC code.

    Provides utilities such as label generation, memory management etc."""
    _INIT_ORIGIN = 0x00
    _FUNCTION_SPACE_ORIGIN = 0x200
    _FUNCTION_SPACE_INCREMENT = 0x500
    _DATA_SPACE_ORIGIN = 0x1000
    _INITIAL_STACK_POINTER = 0x40000

    FUNCTION_SPACE_POINTER = _FUNCTION_SPACE_ORIGIN
    DATA_SPACE_POINTER = _DATA_SPACE_ORIGIN

    FUNCTION_LABEL_COUNT = 0
    DATA_LABEL_COUNT = 0
    GENERIC_LABEL_COUNT = 0

    _function_labels = {}

    MAIN_LABEL = 0

    _header_code = []
    _main_call_code = []
    _code = []
    _trailer_code = []

    @staticmethod
    def get_next_function_label():
        current = FRISC.FUNCTION_LABEL_COUNT
        FRISC.FUNCTION_LABEL_COUNT += 1
        return 'FUNC_{}'.format( current )

    @staticmethod
    def get_next_data_label():
        current = FRISC.DATA_LABEL_COUNT
        FRISC.DATA_LABEL_COUNT += 1
        return 'DATA_{}'.format( current )

    @staticmethod
    def get_next_generic_label( label = 'LABL'):
        current = FRISC.GENERIC_LABEL_COUNT
        FRISC.GENERIC_LABEL_COUNT += 1
        return '{}_{}'.format( label, current )

    @staticmethod
    def get_function_label( name ):
        if name not in FRISC._function_labels:
            FRISC._function_labels[ name ] = FRISC.get_next_function_label()
        return FRISC._function_labels[ name ]

    @staticmethod
    def get_next_function_location( size ):
        current = FRISC.FUNCTION_SPACE_POINTER
        FRISC.FUNCTION_SPACE_POINTER += size
        return current

    @staticmethod
    def get_next_data_location( size ):
        current = FRISC.DATA_SPACE_POINTER
        FRISC.DATA_SPACE_POINTER += size
        return current

    @staticmethod
    def register_main_function( label ):
        FRISC.MAIN_LABEL = label

    @staticmethod
    def generate_header():
        FRISC._header_code += [ '\t`ORG 0{:X}'.format( FRISC._INIT_ORIGIN ), '\tMOVE 0{:X}, SP'.format( FRISC._INITIAL_STACK_POINTER ) ]

    @staticmethod
    def generate_main_call():
        FRISC._main_call_code += [ '\tCALL {}'.format( FRISC.MAIN_LABEL ), '\tHALT', '' ]

    @staticmethod
    def generate_extra_operators():
        FRISC._code += [ 'MULTPL', '\tMOVE 0, R6', 'MULOOP', '\tCMP R2, 0', '\tJP_Z MULEND', '\tADD R6, R1, R6', '\tSUB R2, 1, R2', '\tJP MULOOP', 'MULEND', '\tRET', '' ]
        FRISC._code += [ 'DIVIDE', '\tMOVE 0, R6', 'DIVLOP', '\tSUB R1, R2, R1', '\tJP_ULT DIVEND', '\tADD R6, 1, R6', '\tJP DIVLOP', 'DIVEND', '\tRET', '' ]
        FRISC._code += [ 'MODULO', '\tSUB R1, R2, R1', '\tJP_ULT MODEND', '\tJP MODULO', 'MODEND', '\tADD R1, R2, R6', '\tRET', '' ]

    @staticmethod
    def generate_final_code():
        FRISC._code = FRISC._header_code + FRISC._main_call_code + FRISC._code + FRISC._trailer_code

    @staticmethod
    def output_final_code():
        print( ';' + '='*10 + ' OUTPUT MADE BY friscGEN 1.0.1 ' + '='*60 + ';' )
        for line in FRISC._code:
            print( line )

    @staticmethod
    def place_code_in_global_scope( code ):
        FRISC._header_code += code

    @staticmethod
    def place_function_in_memory( code ):
        FRISC._code += code

    @staticmethod
    def place_data_in_memory( code ):
        FRISC._trailer_code += code


################################################################################
# Building blocks                                                              #
################################################################################

# Type definitions; ignoring consts; all variables will be of size 4 ###########

class Type:
    @staticmethod
    def is_array():     raise TypeError
    @staticmethod
    def to_array():     raise TypeError
    @staticmethod
    def from_array():   raise TypeError
    @staticmethod
    def size():         raise NotImplementedError

class Undefined( Type ):pass

class Int( Type ):
    @staticmethod
    def is_array():     return False
    @staticmethod
    def to_array():     return IntArray
    @staticmethod
    def size():         return 4

class Char( Type ):
    @staticmethod
    def is_array():     return False
    @staticmethod
    def to_array():     return CharArray
    @staticmethod
    def size():         return 4

class IntArray( Type ):
    @staticmethod
    def is_array():     return True
    @staticmethod
    def from_array():   return Int
    @staticmethod
    def size( length ): return 4*length

class CharArray( Type ):
    @staticmethod
    def is_array():     return True
    @staticmethod
    def from_array():   return Char
    @staticmethod
    def size( length ): return 4*length

class Void( Type ):
    @staticmethod
    def is_array():     return False
    @staticmethod
    def size():         return 0

class FunctionType( Type ):
    def __init__( self, return_type, argument_types = Void ):
        self.return_type = return_type
        self.argument_types = argument_types
    def is_array( self ):     return False
    def size( self ):         return len( self.argument_types ) * 4 if self.argument_types != Void else 0
    def __str__( self ):      return '{} => {}'.format( self.argument_types, self.return_type )


# Value definitions and basic operations #######################################

class Value:
    def place_on_stack( self ): raise NotImplementedError

class VoidValue( Value ):
    def place_on_stack( self ): raise NotImplementedError # return []

class ArrayAccess( Value ):
    def __init__( self, variable, index ):
        self.variable = variable
        self.index = index
    def place_on_stack( self ):
        code = [ ';=== Array element loading ===;' ]
        code += self.variable.place_on_stack()
        code += [ '\tPOP R4' ]
        code += self.index.place_on_stack()
        code += [ '\tPOP R1', '\tSHL R1, 2, R1', '\tADD R4, R1, R4', '\tLOAD R0, (R4)', '\tPUSH R0' ]
        return code
    def store_from_stack( self ):
        code = [ ';=== Array element storing ===;' ]
        code += self.variable.place_on_stack()
        code += [ '\tPOP R4' ]
        code += self.index.place_on_stack()
        code += [ '\tPOP R1', '\tSHL R1, 2, R1', '\tADD R4, R1, R4', '\tPOP R0', '\tSTORE R0, (R4)' ]
        return code

class TopOfStack( Value ):
    def place_on_stack( self ): return []

class Number( Value ):
    def __init__( self, value ):    self.value = value
    def place_on_stack( self ):     return [ '\tMOVE 0{:X}, R0'.format( self.value ), '\tPUSH R0' ]

class Constant( Value ):
    def __init__( self, const_value, const_type, array_size = None ):
        self.value = const_value
        self.type = const_type
        self.array_size = array_size
        self.is_array = array_size is not None

        if self.is_array: raise NotImplementedError

        self.label = FRISC.get_next_data_label()
        self.location = FRISC.get_next_data_location( 4 )

        bvals = []
        tvalue = self.value
        for i in range( 4 ):
            bvals.append( tvalue & 255 )
            tvalue >>= 8
        FRISC.place_data_in_memory( [ '\t`ORG 0{:X}'.format( self.location ), self.label,
            '\t`DW 0{:X}, 0{:X}, 0{:X}, 0{:X}'.format( bvals[ 0 ], bvals[ 1 ], bvals[ 2 ], bvals[ 3 ] ), '' ] )

    def place_on_stack( self ):
        if self.type.is_array(): raise ValueError( 'Cannot push array on stack' )
        return [ '\tLOAD R0, ({})'.format( self.label ), '\tPUSH R0' ]

class Variable( Value ):
    def __init__( self, var_name, var_type, load_key = None, array_size = None ):
        self.name = var_name
        self.type = var_type
        self.load_key = load_key
        self.array_size = array_size
        self.is_array = array_size is not None
    def place_on_stack( self ):
        if not self.load_key: raise ValueError( 'Unknown location' )
        if self.is_array:
            return ( [ '\tMOVE {}, R0'.format( self.load_key[ 1: ] ), '\tPUSH R0' ] if self.load_key[ 0 ] == '#'
                else [ '\tMOVE {}, R0'.format( self.load_key.split( '-' )[ 1 ] ), '\tSUB R5, R0, R0', '\tPUSH R0' ] )
        else:
            return [ '\tLOAD R0, {}'.format( self.load_key ), '\tPUSH R0' ]
    def store_from_stack( self ):
        if not self.load_key: raise ValueError( 'Unknown location' )
        return [ '\tPOP R0', '\tSTORE R0, {}'.format( self.load_key ) ]
    def __repr__( self ):   return '{} :: {}@{}'.format( self.name, self.type, self.load_key )

class FunctionParameter:
    def __init__( self, param_name, param_type ):
        self.name = param_name
        self.type = param_type
    def __repr__( self ): return '{} {}'.format( self.name, self.type )

class Function:
    def __init__( self, func_name, func_type ):
        self.name = func_name
        self.type = func_type
        self.label = FRISC.get_function_label( self.name )
        self.location = None

    def __str__( self ):                return '{} :: {}; {}@{}'.format( self.name, self.type, self.label, self.location )
    def create_location( self, size ):  self.location = FRISC.get_next_function_location( size )
    def get_result( self ):             return VoidValue() if self.type.return_type == Void else TopOfStack()
    def call( self, params = [] ):      # Pushing parameters in definition order, then calling function, afterwards popping params
        code = [ ';=== Calling {} ===;'.format( self.name ) ]
        for var in params:
            code += var.place_on_stack()
        code += [ '\tCALL ' + self.label, '\tADD SP, 0{:X}, SP'.format( len( params )*4 ) ]
        #if self.type.return_type != Void:
        code += [ '\tPUSH R6' ]
        code += [ ';=== Returned from {} ===;'.format( self.name ) ]
        return code


# Scoping ######################################################################

class Scope:
    """Represents a name => object mapping of a program section"""
    _scope_count = 0

    def __init__( self, parent = None ):
        self.parent = parent
        self.identifiers = {}
        self.depth = self.parent.depth+1 if parent is not None else 0
        self.scope_num = Scope._scope_count
        self.local_vars = 0
        Scope._scope_count += 1

    def __str__( self ):                    return 'Scope {}[{}] :: {}'.format( self.scope_num, self.depth, self.identifiers )
    def __contains__( self, name ):         return True if name in identifiers else ( name in self.parent if self.parent is not None else False )
    def __getitem__( self, name ):          return self.identifiers[ name ] if name in self.identifiers else ( self.parent[ name ] if self.parent is not None else None )
    def __setitem__( self, name, value ):   self.identifiers[ name ] = value
    def get_local_vars( self ):             return ( self.local_vars + 4 ) if self.depth < 2 else self.parent.get_local_vars()
    def make_local_var( self, size ):
        if self.depth > 1: self.parent.make_local_var( size )
        else: self.local_vars += size


# Labelling ####################################################################

class Labels:
    def __init__( self, ret_label, loop_label = None, end_loop_label = None ):
        self.ret = ret_label
        self.loop = loop_label
        self.end_loop = end_loop_label

################################################################################
# Generator utilities                                                          #
################################################################################

class TokenLine:
    def __init__( self, name, line, content ):
        self.name = name
        self.line = int( line )
        self.content = content
    def __str__( self ):    return '{} ( {} )'.format( self.name, self.content )
    def __repr__( self ):   return '{}({},{})'.format( self.name, self.line, self.content )
    def get_type( self ):
        if self.name == 'BROJ':             return Int
        elif self.name == 'ZNAK':           return Char
        elif self.name == 'NIZ_ZNAKOVA':    return CharArray
        else:                               return Undefined

class UnitLine:
    def __init__( self, name ):     self.name = name
    def __str__( self ):            return self.name
