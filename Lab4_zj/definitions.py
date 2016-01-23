################################################################################
# Utilities                                                              #
################################################################################

class FRISC:
    """Helper class having only static methods dealing with properties of resulting FRISC code.

    Provides utilities such as label generation, memory management etc."""
    _INIT_ORIGIN = 0x00
    _FUNCTION_SPACE_ORIGIN = 0x50
    _FUNCTION_SPACE_INCREMENT = 0x500
    _DATA_SPACE_ORIGIN = 0x1000
    _INITIAL_STACK_POINTER = 0x40000

    FUNCTION_SPACE_POINTER = _FUNCTION_SPACE_ORIGIN
    DATA_SPACE_POINTER = _DATA_SPACE_ORIGIN

    FUNCTION_LABEL_COUNT = 0
    VALUE_LABEL_COUNT = 0
    GENERIC_LABEL_COUNT = 0

    _function_labels = {}

    MAIN_LABEL = 0

    _header_code = []
    _code = []
    _trailer_code = []

    @staticmethod
    def get_next_function_label():
        current = FRISC.FUNCTION_LABEL_COUNT
        FRISC.FUNCTION_LABEL_COUNT += 1
        return 'FUNC_{}'.format( current )

    @staticmethod
    def get_next_variable_label():
        current = FRISC.VARIABLE_LABEL_COUNT
        FRISC.VARIABLE_LABEL_COUNT += 1
        return 'DATA_{}'.format( current )

    @staticmethod
    def get_next_generic_label():
        current = FRISC.GENERIC_LABEL_COUNT
        FRISC.GENERIC_LABEL_COUNT += 1
        return 'LABL_{}'.format( current )

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
    def generate_skeleton():
        FRISC._header_code += [
            '\tORG {:X}'.format( FRISC._INIT_ORIGIN ),
            '\tMOVE {:X}, SP'.format( FRISC._INITIAL_STACK_POINTER ),
            '\tCALL {}'.format( FRISC.MAIN_LABEL ),
            '\tHALT',
            '' ]

    @staticmethod
    def generate_final_code():
        FRISC._code = FRISC._header_code + FRISC._code + FRISC._trailer_code

    @staticmethod
    def output_final_code():
        print( ';' + '='*10 + ' OUTPUT MADE BY friscGEN 1.0.1 ' + '='*60 )
        for line in FRISC._code:
            print( line )

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

class TopOfStack( Value ):
    def place_on_stack( self ): return []

class Constant( Value ):
    def __init__( self, const_value, const_type ):
        self.value = const_value
        self.type = const_type

    def place_on_stack( self ):
        if self.type.is_array(): raise ValueError( 'Cannot push array on stack' )
        return [ '\tLOAD R0, ({})'.format(), '\tPUSH R0' ]

class Variable( Value ):
    def __init__( self, var_name, var_type, load_key = None ):
        self.name = var_name
        self.type = var_type
        self.load_key = load_key
    def place_on_stack( self ):
        if not self.load_key: raise ValueError( 'Unknown location' )
        return [ '\tLOAD R0, ({})'.format( self.load_key ), '\tPUSH R0' ]        

class FunctionParameter:
    def __init__( self, param_name, param_type ):
        self.name = param_name
        self.type = param_type
    def __repr__( self ): return '{} {}'.format( self.name, self.type )

class Function:
    def __init__( self, func_name, func_type, defined ):
        self.name = func_name
        self.type = func_type
        self.label = FRISC.get_function_label( self.name )
        self.location = None

    def __str__( self ): return '{} :: {}; {}@{}'.format( self.name, self.type, self.label, self.location )
    def create_location( self, size ): self.location = FRISC.get_next_function_location( size )
    def call( self, params ):   # Pushing parameters in reverse order, then calling function, afterwards popping params
        code = []
        for var in reversed( params ):
            code += var.place_on_stack()
        code += [ '\tCALL ' + self.label, '\tADD SP, {}, SP'.format( len( params )*4 ) ]
        return code


# Scoping ######################################################################

class Scope:
    """Represents a name => object mapping of a program section"""
    _scope_count = 0

    def __init__( self, parent = None ):
        self.parent = parent
        self.identifiers = {}
        self.depth = self.parent.depth if parent is not None else 0
        self.scope_num = Scope._scope_count
        self.local_vars = 0
        Scope._scope_count += 1

    def __str__( self ):                    return 'Scope {} :: {}'.format( self.scope_num, self.identifiers )
    def __contains__( self, name ):         return True if name in identifiers else ( name in self.parent if self.parent is not None else False )
    def __getitem__( self, name ):          return self.identifiers[ name ] if name in self.identifiers else ( self.parent[ name ] if self.parent is not None else None )
    def __setitem__( self, name, value ):   self.identifiers[ name ] = value
    def make_local_var( self, size ):       if self.depth > 1: self.parent.make_local_var( size )
                                            else: self.local_vars += size


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
