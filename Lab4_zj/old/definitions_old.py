"""
    Basic building blocks for semantic analysis and code generation.

        :: Lines, Types, Variables, Arguments, Functions, Scopes

"""
from abc import ABC, ABCMeta, abstractmethod

################################################################################

class TokenLine:
    def __init__( self, name, line, content ):
        self.name = name
        self.line = int( line )
        self.content = content
    # def __str__( self ):
    #     return '{} ( {} )'.format( self.name, self.content )
    def __repr__( self ):
        return '{}({},{})'.format( self.name, self.line, self.content )
    def get_type( self ):
        if self.name == 'BROJ': return Int
        elif self.name == 'ZNAK': return Char
        elif self.name == 'NIZ_ZNAKOVA': return ConstCharArray
        else: return Undefined

class UnitLine:
    def __init__( self, name ):
        self.name = name
    def __str__( self ):
        return self.name

################################################################################

class Type:
    const = False
    lvalue = False

    @staticmethod
    def to_const(): return TypeError

    @staticmethod
    def from_const(): return TypeError

    @staticmethod
    def to_array(): return TypeError

    @staticmethod
    def from_array(): return TypeError

    @staticmethod
    def is_array(): return False

    @staticmethod
    def validate( value ): return TypeError

    def __str__( self ):
        return self.__class__

class Undefined( Type ): pass

class Int( Type ):
    const = False
    lvalue = True

    @staticmethod
    def to_const(): return ConstInt

    @staticmethod
    def to_array(): return IntArray

    @staticmethod
    def validate( value ):
        try:
            value = int( value )
            return ( value >= -(1<<31)) and ( value < (1<<31) )
        except:
            return False

class ConstInt( Int ):
    const = True
    lvalue = False

    @staticmethod
    def from_const(): return Int

    @staticmethod
    def to_array(): return ConstIntArray

class Char( Int ):
    const = False
    lvalue = True

    @staticmethod
    def to_const(): return ConstChar

    @staticmethod
    def to_array(): return CharArray

    @staticmethod
    def validate( value ):  # Expecting "a" or "\x"
        if value[ 1 ] == '\\':
            return len( value ) == 4 and value[ 2 ] in '\'\"nt0\\'
        else:
            return len( value ) == 3

class ConstChar( Char ):
    const = True
    lvalue = False

    @staticmethod
    def from_const(): return Char

    @staticmethod
    def to_array(): return ConstCharArray

class Array( Type ):

    @staticmethod
    def is_array(): return True

class IntArray( Array ):

    @staticmethod
    def to_const(): return ConstIntArray

    @staticmethod
    def from_array(): return Int

    @staticmethod
    def validate( value ): pass

class ConstIntArray( IntArray ):

    @staticmethod
    def from_const(): return IntArray

    @staticmethod
    def from_array(): return ConstInt


class CharArray( Array ):

    @staticmethod
    def to_const():
        return ConstCharArray

    @staticmethod
    def from_array(): return Char

    @staticmethod
    def validate( value ):
        escaped = False
        for c in value[ 1:-1 ]:
            if escaped and c not in '\'\"nt0\\': return False
            elif c == '\\': escaped = not escaped
            else: escaped = False
        return not escaped

class ConstCharArray( CharArray ):

    @staticmethod
    def from_const(): return CharArray

    @staticmethod
    def from_array(): return ConstChar

class Void( Type ):
    const = None

    @staticmethod
    def validate( value ):  raise TypeError

class FunctionType( Type ):
    def __init__( self, rtype, argtypes = Void ):
        self.return_type = rtype
        self.argument_types = argtypes


################################################################################
#  Use for code generation - pass variables and expressions up the tree,       #
#  or use stack.                                                               #
################################################################################

class Value: pass        # Defines location of an expression return value

class TOS( Value ): pass # Top Of Stack

class Constant( Value ):
    def __init__( self, ctype ):
        self.type = ctype
        self.address = None
        self.size = 0

class Variable( Value ):
    def __init__( self, vname, vtype = Undefined, array_size = None, formal = False ):
        self.name = vname
        self.type = vtype
        self.address = None
        self.size = 0
        self.array_size = array_size
        self.formal = formal

    def __repr__( self ):
        return '{} {}{} :: {}'.format( self.type, self.name, ( '[ {} ]'.format( self.array_size ) if self.array_size is not None else '' ), self.formal )

class FunctionArgument:
    def __init__( self, aname, atype ):
        self.name = aname
        self.type = atype

class Function:
    def __init__( self, name, ftype, arguments = None, defined = False ):
        self.name = name
        self.type = ftype
        self.arguments = arguments
        self.defined = defined
        self.address = None
        self.size = 0

    def __repr__( self ):
        return '{} {}( {} ) :: {}'.format( self.type.return_type, self.name, self.type.argument_types, self.defined )

class Scope:
    _scope_count = 0

    def __init__( self, parent = None ):
        self.parent = parent
        self.identifiers = {}
        self.scope_num = Scope._scope_count
        Scope._scope_count += 1

    def __str__( self ):
        return 'Scope {} :: {}'.format( self.scope_num, self.identifiers )

    def __getitem__( self, name ):
        if name in self.identifiers:
            return self.identifiers[ name ]
        return self.parent[ name ] if self.parent is not None else None

    def __setitem__( self, name, value ):
        self.identifiers[ name ] = value

    def __contains__( self, name ):
        if name in self.identifiers:
            return True
        return name in self.parent if self.parent is not None else False

    def insert( self, item ):
        self.identifiers[ item.name ] = item
