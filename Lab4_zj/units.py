from definitions import *


class Unit:
    def __init__( self, depth, scope ):
        self.depth = depth
        self.children = []
        self.scope = scope

    def __str__( self ):
        return (
            ' '*self.depth + '{} :: {} => [\n'.format( self.depth, self.__class__ ) +
            '\n'.join( map( str, self.children ) ) + '\n' +
            ' '*self.depth + ']'
        )

    def __repr__( self ):
        return str( self )

    def __len__( self ):
        return len( self.children )

    def __getitem__( self, key ):
        return self.children[ key ]

    def generate( self ):
        pass

    def process( self ):
        pass

    def append( self, child ):
        self.children.append( child )

class Token( Unit ):
    def __init__( self, token, depth ):
        self.token = token
        super().__init__( depth, None )

    def __str__( self ):
        return ' '*self.depth + str( self.token )

################################################################################

class CompilationUnit( Unit ): pass

class ExternalDeclaration( Unit ): pass

class FunctionDefinition( Unit ):
    def __init__( self, depth, scope ):
        super().__init__( depth, scope )
        self.type = Undefined

    def process( self ):
        if len( self ) == 6:    # TypeName IDN ( VOID ) ComplexInstruction
            self.type = FunctionType( self[ 0 ].type, Void )
            self.scope[ self[ 1 ].token.content ] = Function( self[ 1 ].token.content, self.type, True )
        elif len( self ) == 7:  # TypeName IDN ( ArgumentList ) ComplexInstruction
            # TODO
            pass


class ParameterList( Unit ): pass

class ParameterDeclaration( Unit ): pass

################################################################################

class AbstractInstruction( Unit ):
    def __init__( self, depth, scope ):
        super().__init__( depth, scope )
        self.type = Undefined

class ComplexInstruction( Unit ):
    def __init__( self, depth, scope ):
        scope = Scope( scope )
        super().__init__( depth, scope )
        # self.return_value = Void

class InstructionList( Unit ): pass # ??

class Instruction( AbstractInstruction ): pass

class ExpressionInstruction( AbstractInstruction ):
    def process( self ):
        if len( self ) == 1:    # ;
            self.type = Int
        elif len( self ) == 2:  # Expression ;
            self.type = self[ 0 ].type

class BranchInstruction( AbstractInstruction ):
    def process( self ):
        if len( self ) == 5:    # IF ( Expression ) Instruction
            pass
        elif len( self ) == 7:  # IF ( Expression ) Instruction ELSE Instruction
            pass

class LoopInstruction( AbstractInstruction ):
    def process( self ):
        if len( self ) == 5:    # WHILE ( Expression ) Instruction
            pass
        elif len( self ) == 6:  # FOR ( ExpressionInstruction ExpressionInstruction ) Instruction
            pass
        elif len( self ) == 7:  # FOR ( ExpressionInstruction ExpressionInstruction Expression ) Instruction
            pass

class JumpInstruction( AbstractInstruction ):
    def process( self ):
        if self[ 0 ].token.name == 'KR_BREAK':
            pass
        elif self[ 0 ].token.name == 'KR_CONTINUE':
            pass
        elif self[ 0 ].token.name == 'KR_RETURN':
            if len( self ) == 2:    # RETURN ;
                pass
            elif len( self ) == 3:  # RETURN Expression ;
                pass

################################################################################

class DeclarationList( Unit ): pass

class Declaration( Unit ): pass

class InitDeclarationList( Unit ): pass

class InitDeclaration( Unit ): pass

class DirectDeclarator( Unit ): pass

class Initializer( Unit ): pass

class AssignmentExpressionList( Unit ): pass

class ArgumentList( Unit ):
    def __init__( self, depth, scope ):
        super().__init__( depth, scope )
        self.types = []

    def process( self ):
        if len( self ) == 1:    # ( x )
            self.types = [ self[ 0 ].type ]
        else:   # ( x, ArgumentList )
            self.types = self[ 0 ].types + [ self[ 2 ].type ]


################################################################################

class AbstractExpression( Unit ):
    def __init__( self, depth, scope ):
        super().__init__( depth, scope )
        self.type = Undefined
        self.lvalue = None

class Expression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # AssignmentExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # Expression , AssignmentExpression
            self.type = self[ 2 ].type
            self.lvalue = True

class AssignmentExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # LogicalOrExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # PostfixExpression || AssignmentExpression
            self.type = self[ 0 ].type
            self.lvalue = False

class PostfixExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # PrimaryExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 2:  # x++ or x--
            self.type = Int
            self.lvalue = False
        elif len( self ) == 3:  # func ()
            self.type = self[ 0 ].type.return_type
            self.lvalue = False
        elif len( self ) == 4:
            if self[ 1 ].token.name == 'L_UGL_ZAGRADA':     # array[]
                self.type = self[ 0 ].type.element_type
                self.lvalue = not self.type.const
            elif self[ 1 ].token.name == 'L_ZAGRADA':       # func( args )
                self.type = self[ 0 ].type.return_type
                self.lvalue = False


class PrimaryExpression( AbstractExpression ):
    def process( self ):
        if self[ 0 ].token.name == 'IDN':
            self.type = self.scope[ self[ 0 ].token.content ].type   # KeyError possible
            self.lvalue = self.type.lvalue
        elif self[ 0 ].token.name == 'BROJ':
            if not Int.validate( self[ 0 ].token.content ): raise ValueError( 'Not a valid integer.' )
            self.type = Int
            self.lvalue = False
        elif self[ 0 ].token.name == 'ZNAK':
            if not Char.validate( self[ 0 ].token.content ): raise ValueError( 'Not a valid char.' )
            self.type = Char
            self.lvalue = False
        elif self[ 0 ].token.name == 'NIZ_ZNAKOVA':
            if not ConstCharArray.validate( self[ 0 ].token.content ): raise ValueError( 'Not a valid string.' )
            self.type = ConstCharArray
            self.lvalue = False
        elif len( self ) == 3:   # ( Expression )
            self.type = self[ 1 ].type
            self.lvalue = self[ 1 ].type

class LogicalOrExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # LogicalAndExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # LogicalOrExpression || LogicalAndExpression
            self.type = Int
            self.lvalue = False

class LogicalAndExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # BinaryOrExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # LogicalAndExpression && BinaryOrExpression
            self.type = Int
            self.lvalue = False

class BinaryOrExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # BinaryXorExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # BinaryOrExpression | BinaryXorExpression
            self.type = Int
            self.lvalue = False

class BinaryXorExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # BinaryAndExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # BinaryXorExpression ^ BinaryAndExpression
            self.type = Int
            self.lvalue = False

class BinaryAndExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # EqualityExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # BinaryAndExpression & EqualityExpression
            self.type = Int
            self.lvalue = False

class EqualityExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # RelationalExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # EqualityExpression (==|!=) RelationalExpression
            self.type = Int
            self.lvalue = False

class RelationalExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # AdditiveExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # RelationalExpression (<|>|<=|>=) AdditiveExpression
            self.type = Int
            self.lvalue = False

class AdditiveExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # MultiplicativeExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # AdditiveExpression (+|-) MultiplicativeExpression
            self.type = Int
            self.lvalue = False


class MultiplicativeExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # CastExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 3:  # MultiplicativeExpression (*|/|%) CastExpression
            self.type = Int
            self.lvalue = False

class CastExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # UnaryExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 4:  # ( TypeName ) CastExpression
            self.type = self[ 1 ].type
            self.lvalue = False

class UnaryExpression( AbstractExpression ):
    def process( self ):
        if len( self ) == 1:    # PostfixExpression
            self.type = self[ 0 ].type
            self.lvalue = self[ 0 ].lvalue
        elif len( self ) == 2:
            if isinstance( self[ 0 ], Token ):  # (++ | --) UnaryExpression
                self.type = Int
                self.lvalue = False
            elif isinstance( self[ 0 ], UnaryOperator ):    # UnaryOperator UnaryExpression
                self.type = Int
                self.lvalue = False



################################################################################

class UnaryOperator( Unit ):
    pass

class TypeName( Unit ):
    def __init__( self, depth, scope ):
        super().__init__( depth, scope )
        self.type = Undefined

    def process( self ):
        if len( self ) == 1:    # TypeSpecifier
            self.type = self[ 0 ].type
        elif len( self ) == 2:  # const TypeSpecifier
            self.type = self[ 0 ].type.to_const()

class TypeSpecifier( Unit ):
    def __init__( self, depth, scope ):
        super().__init__( depth, scope )
        self.type = Undefined

    def process( self ):
        if self[ 0 ].token.name == 'KR_VOID':
            self.type = Void
        elif self[ 0 ].token.name == 'KR_INT':
            self.type = Int
        elif self[ 0 ].token.name == 'KR_CHAR':
            self.type = Char

################################################################################

_units = {
    '<prijevodna_jedinica>'         : CompilationUnit,
    '<vanjska_deklaracija>'         : ExternalDeclaration,
    '<definicija_funkcije>'         : FunctionDefinition,
    '<lista_parametara>'            : ParameterList,
    '<deklaracija_parametara>'      : ParameterDeclaration,
    '<slozena_naredba>'             : ComplexInstruction,
    '<lista_naredbi>'               : InstructionList,
    '<naredba>'                     : Instruction,
    '<izraz_naredba>'               : ExpressionInstruction,
    '<naredba_grananja>'            : BranchInstruction,
    '<naredba_petlje>'              : LoopInstruction,
    '<naredba_skoka>'               : JumpInstruction,
    '<lista_deklaracija>'           : DeclarationList,
    '<deklaracija>'                 : Declaration,
    '<lista_init_deklaratora>'      : InitDeclarationList,
    '<init_deklarator>'             : InitDeclaration,
    '<izravni_deklarator>'          : DirectDeclarator,
    '<inicijalizator>'              : Initializer,
    '<lista_izraza_pridruzivanja>'  : AssignmentExpressionList,
    '<izraz>'                       : Expression,
    '<izraz_pridruzivanja>'         : AssignmentExpression,
    '<postfiks_izraz>'              : PostfixExpression,
    '<primarni_izraz>'              : PrimaryExpression,
    '<lista_argumentata>'           : ArgumentList,
    '<log_ili_izraz>'               : LogicalOrExpression,
    '<log_i_izraz>'                 : LogicalAndExpression,
    '<bin_ili_izraz>'               : BinaryOrExpression,
    '<bin_xili_izraz>'              : BinaryXorExpression,
    '<bin_i_izraz>'                 : BinaryAndExpression,
    '<jednakosni_izraz>'            : EqualityExpression,
    '<odnosni_izraz>'               : RelationalExpression,
    '<aditivni_izraz>'              : AdditiveExpression,
    '<multiplikativni_izraz>'       : MultiplicativeExpression,
    '<cast_izraz>'                  : CastExpression,
    '<unarni_izraz>'                : UnaryExpression,
    '<unarni_operator>'             : UnaryOperator,
    '<ime_tipa>'                    : TypeName,
    '<specifikator_tipa>'           : TypeSpecifier
}

def get_unit( line ):
    return _units[ line ]
