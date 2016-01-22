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
    def __str__( self ):
        return '{} ( {} )'.format( self.name, self.content )
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

class Type( ABC ):
    const = False
    lvalue = False

    @staticmethod
    @abstractmethod
    def to_const(): pass

    @staticmethod
    @abstractmethod
    def from_const(): pass

    @staticmethod
    @abstractmethod
    def validate( value ): pass


class Undefined( Type ):
    @staticmethod
    def to_const(): raise TypeError

    @staticmethod
    def from_const(): raise TypeError

    @staticmethod
    def validate( value ): raise TypeError


class Int( Type ):
    const = False
    lvalue = True

    @staticmethod
    def to_const():
        return ConstInt

    @staticmethod
    def from_const():
        return Int

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

class Char( Int ):
    const = False
    lvalue = True

    @staticmethod
    def to_const():
        return ConstChar

    @staticmethod
    def from_const():
        return Char

    @staticmethod
    def validate( value ):  # Expecting "a" or "\x"
        if value[ 1 ] == '\\':
            return len( value ) == 4 and value[ 2 ] in '\'\"nt0\\'
        else:
            return len( value ) == 3


class ConstChar( Char ):
    const = True
    lvalue = False

class Array( Type ):
    element_type = None


class IntArray( Array ):
    element_type = Int

    @staticmethod
    def to_const():
        return ConstIntArray

    @staticmethod
    def from_const():
        return IntArray

    @staticmethod
    def validate( value ): pass

class ConstIntArray( IntArray ):
    element_type = ConstInt


class CharArray( Array ):
    element_type = Char

    @staticmethod
    def to_const():
        return ConstCharArray

    @staticmethod
    def from_const():
        return CharArray

    @staticmethod
    def validate( value ):
        escaped = False
        for c in value[ 1:-1 ]:
            if escaped and c not in '\'\"nt0\\': return False
            elif c == '\\': escaped = not escaped
            else: escaped = False
        return not escaped


class ConstCharArray( CharArray ):
    element_type = ConstChar


class Void( Type ):
    const = None

    @staticmethod
    def to_const(): raise TypeError

    @staticmethod
    def from_const():  raise TypeError

    @staticmethod
    def validate( value ):  raise TypeError

class ArgumentTypesList:
    def __init__( self, args = None ):
        self.argument_types = args if args is not None else Void

class FunctionType:
    def __init__( self, rtype, argtypes ):
        self.return_type = rtype
        self.argument_types = argtypes

################################################################################
#  Use for code generation - pass variables and expressions up the tree,       #
#  or use stack.                                                               #
################################################################################

class Constant:
    def __init__( self, ctype ):
        self.type = ctype
        self.address = None
        self.size = 0

class Variable:
    def __init__( self, vname, vtype = Undefined ):
        self.name = vname
        self.type = vtype
        self.address = None
        self.size = 0

# TODO: Rethink functions

class FunctionArgument:
    def __init__( self, aname, atype = Undefined ):
        self.name = aname
        self.type = atype

class FunctionArgumentsList:
    def __init__( self, *args ):
        self.arguments = args

    def append( self, arg ):
        self.arguments.append( arg )

class Function:
    def __init__( self, name, ftype, defined = False ):
        self.name = name
        self.type = ftype
        self.defined = defined
        self.address = None

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
        return self.parent[ 'name' ] if self.parent is not None else None

    def __setitem__( self, name, value ):
        self.identifiers[ name ] = value

    def __contains__( self, name ):
        if name in self.identifiers:
            return True
        return name in self.parent if self.parent is not None else False

    def insert( self, item ):
        self.identifiers[ item.name ] = item
