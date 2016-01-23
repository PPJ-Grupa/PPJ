from definitions import *

################################################################################
# Basic units                                                                  #
################################################################################

class Unit:
    def __init__( self, depth ):
        self.depth = depth
        self.children = []

    def __str__( self ):            return '{}{} :: {} => [\n{}\n{}]'.format( ' '*self.depth, self.depth, self.__class__,
                                        '\n'.join( map( str, self.children ) ), ' '*self.depth )
    def __repr__( self ):           return str( self )
    def __len__( self ):            return len( self.children )
    def __getitem__( self, key ):   return self.children[ key ]
    def append( self, child ):      self.children.append( child )
    def descend( self, scope ):     [ child.descend( scope ) for child in self.children ]

class Token( Unit ):
    def __init__( self, depth, token ):
        super().__init__( depth )
        self.name = token.name
        self.content = token.content
    def __str__( self ):            return '{}{} :: {} :: {} {}'.format( ' '*self.depth, self.depth, self.__class__, self.name, self.content )

class AbstractExpression( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.result = None
        self.type = Undefined

class AbstractInstruction( Unit ):
    pass
    # Have a parent loop label name

################################################################################
# Semantic units                                                               #
################################################################################

class CompilationUnit( Unit ):      pass  # ExternalDeclaration | CompilationUnit ExternalDeclaration
class ExternalDeclaration( Unit ):  pass  # FunctionDefinition | Declaration

class FunctionDefinition( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.function = None
        self.parameters = []

    def descend( self, scope ): # TypeName IDN ( VOID | ParameterList ) ComplexInstruction
        super().descend( scope )
        self.parameters = self[ 3 ].parameters if isinstance( self[ 3 ], ParameterList ) else []
        parameter_types = [ param.type for param in self.parameters ] if self.parameters else Void

        self.function = Function( self[ 1 ].content, FunctionType( self[ 0 ].type, parameter_types ), True )
        scope[ self[ 1 ].content ] = self.function
        if self.function.name == 'main': FRISC.register_main_function( self.function.label )

        local_scope = Scope( scope )
        for i, param in enumerate( self.parameters ):
            local_scope[ param.name ] = Variable( param.name, param.type, load_key = '(R5-{:X})'.format( 4*( 2+i ) ) )

        child_code = self[ 5 ].descend( local_scope )
        self.function.create_location( 16 + len( child_code ) )

        code = [ '', '\tORG {:X}'.format( self.function.location ), self.function.label, '\tPUSH R5', '\tMOVE SP, R5' ]
        code += child_code
        code += [ '\tADD SP, {:X}, SP'.format( local_scope.local_vars ), '\tPOP R5', '\tRET' ]

        FRISC.place_function_in_memory( code )

class ParameterList( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.parameters = []

    def descend( self, scope ):     # ParameterDeclaration | ParameterList , ParameterDeclaration
        super().descend( scope )
        self.parameters = ( [ self[ 0 ].parameter ] if len( self ) == 1 else
            ( self[ 0 ].parameters + [ self[ 2 ].parameter ] ) )

class ParameterDeclaration( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.parameter = None

    def descend( self, scope ):
        super().descend( scope )    # TypeName IDN | TypeName IDN []
        self.parameter = FunctionParameter( self[ 1 ].content,
            ( self[ 0 ].type if len( self ) == 2 else self[ 0 ].type.to_array() ) )


class ComplexInstruction( Unit ):
    def descend( self, scope ):     # { InstructionList } | { DeclarationList InstructionList }
        local_scope = Scope( scope )
        return self[ 1 ].descend( local_scope ) + ( self[ 2 ].descend( local_scope ) if len( self ) == 4 else [] )

class InstructionList( Unit ): pass
class Instruction( Unit ): pass
class ExpressionInstruction( Unit ): pass
class BranchInstruction( Unit ): pass
class LoopInstruction( Unit ): pass
class JumpInstruction( Unit ): pass

class DeclarationList( Unit ):
    def descend( self, scope ):     # Declaration | DeclarationList Declaration
        return self[ 0 ].descend( scope ) + ( self[ 1 ].descend( scope ) if len( self ) == 2 else [] )

class Declaration( Unit ):
    def descend( self, scope ):     # TypeName InitDeclaratorList ;
        return self[ 1 ].descend( scope, self[ 0 ].type )

class InitDeclaratorList( Unit ):
    def descend( self, scope, inherited_type ):     # InitDeclarator | InitDeclaratorList , InitDeclarator
        return self[ 0 ].descend( scope, inherited_type ) + ( self[ 1 ].descend( scope, inherited_type ) if len( self ) == 3 else [] )

class InitDeclarator( Unit ):
    def descend( self, scope, inherited_type ):     # DirectDeclarator | DirectDeclarator = Initializer
        code = self[ 0 ].descend( scope, inherited_type )
        if len( self == 3 ): raise NotImplementedError

class DirectDeclarator( Unit ):
    def descend( self, scope, inherited_type ):     # IDN | IDN [ BROJ ] | IDN ( VOID ) | IDN ( ParameterList )
        if len( self ) == 1:                        # Defining an int or a char
            if scope.depth == 0:                    # Global variable
                label = FRISC.get_next_variable_label()
                location = FRISC.get_next_data_location( inherited_type.size )
                var = Variable( self[ 0 ].content, inherited_type, '({})'.format( label ) )
                FRISC.place_data_in_memory( [ '\tORG {:X}'.format( location ), '' ] )
                return []
            else:
                print( scope.local_vars )
                # var = Variable( self[ 0 ].content, inherited_type, '(R5+{:X})'.format(  ) )
                return NotImplementedError


class Initializer( Unit ): pass
class ArgumentList( Unit ): pass

class AssignmentExpressionList( Unit ): pass
class Expression( AbstractExpression ): pass
class AssignmentExpression( AbstractExpression ): pass
class PostfixExpression( AbstractExpression ): pass
class PrimaryExpression( AbstractExpression ): pass
class LogicalOrExpression( AbstractExpression ): pass
class LogicalAndExpression( AbstractExpression ): pass
class BinaryOrExpression( AbstractExpression ): pass
class BinaryXorExpression( AbstractExpression ): pass
class BinaryAndExpression( AbstractExpression ): pass
class RelationalExpression( AbstractExpression ): pass
class EqualityExpression( AbstractExpression ): pass
class AdditiveExpression( AbstractExpression ): pass
class MultiplicativeExpression( AbstractExpression ): pass
class CastExpression( AbstractExpression ): pass
class UnaryExpression( AbstractExpression ): pass

class UnaryOperator( Unit ): pass

class TypeName( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.type = Undefined
    def descend( self, scope ): # TypeSpecifier | CONST TypeSpecifier
        super().descend( scope )
        self.type = self[ 0 ].type if len( self ) == 1 else self[ 1 ].type

class TypeSpecifier( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.type = Undefined
    def descend( self, scope ):
        self.type = { 'KR_VOID' : Void, 'KR_INT' : Int, 'KR_CHAR' : Char }[ self[ 0 ].name ]

################################################################################
# Constructing units from input                                                #
################################################################################

_units = {
    '<prijevodna_jedinica>'         : CompilationUnit,
    '<vanjska_deklaracija>'         : ExternalDeclaration,
    '<definicija_funkcije>'         : FunctionDefinition,
    '<lista_parametara>'            : ParameterList,
    '<deklaracija_parametra>'       : ParameterDeclaration,
    '<slozena_naredba>'             : ComplexInstruction,
    '<lista_naredbi>'               : InstructionList,
    '<naredba>'                     : Instruction,
    '<izraz_naredba>'               : ExpressionInstruction,
    '<naredba_grananja>'            : BranchInstruction,
    '<naredba_petlje>'              : LoopInstruction,
    '<naredba_skoka>'               : JumpInstruction,
    '<lista_deklaracija>'           : DeclarationList,
    '<deklaracija>'                 : Declaration,
    '<lista_init_deklaratora>'      : InitDeclaratorList,
    '<init_deklarator>'             : InitDeclarator,
    '<izravni_deklarator>'          : DirectDeclarator,
    '<inicijalizator>'              : Initializer,
    '<lista_izraza_pridruzivanja>'  : AssignmentExpressionList,
    '<izraz>'                       : Expression,
    '<izraz_pridruzivanja>'         : AssignmentExpression,
    '<postfiks_izraz>'              : PostfixExpression,
    '<primarni_izraz>'              : PrimaryExpression,
    '<lista_argumenata>'            : ArgumentList,
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
