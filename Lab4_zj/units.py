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

class AbstractInstruction( Unit ): pass

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
        self.parameters = self[ 3 ].parameters if isinstance( self[ 3 ], ParameterList ) else []
        parameter_types = [ param.type for param in self.parameters ] if self.parameters else Void

        self.function = Function( self[ 1 ].content, FunctionType( self[ 0 ].type, parameter_types ) )
        scope[ self[ 1 ].content ] = self.function
        if self.function.name == 'main': FRISC.register_main_function( self.function.label )

        local_scope = Scope( scope )
        for i, param in enumerate( self.parameters ):
            local_scope[ param.name ] = Variable( param.name, param.type, load_key = '(R5-{:X})'.format( 4*( 2+i ) ) )

        labels = Labels( FRISC.get_next_generic_label() )

        child_code = self[ 5 ].descend( local_scope, labels )
        self.function.create_location( 24 + 4*len( child_code ) )

        code = [ '\tORG {:X}'.format( self.function.location ), self.function.label, '\tPUSH R5', '\tMOVE SP, R5', '\tSUB SP, {:X}, SP'.format( local_scope.local_vars ) ]
        code += child_code
        code += [ labels.ret, '\tADD SP, {:X}, SP'.format( local_scope.local_vars ), '\tPOP R5', '\tRET', '' ]

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
    def descend( self, scope, labels ):     # { InstructionList } | { DeclarationList InstructionList }
        local_scope = Scope( scope )
        if len( self ) == 3: return self[ 1 ].descend( local_scope, labels )
        return self[ 1 ].descend( local_scope ) + self[ 2 ].descend( local_scope, labels )

class InstructionList( Unit ):
    def descend( self, scope, labels ):
        code = []
        for child in self.children:
            code += child.descend( scope, labels )
        return code

class Instruction( Unit ):
    def descend( self, scope, labels ):
        return self[ 0 ].descend( scope, labels )

class ExpressionInstruction( Unit ):
    def descend( self, scope, labels ):     # ; | Expression ;
        if len( self == 1 ): return []
        return self[ 0 ].descend( scope )

class BranchInstruction( Unit ):
    def descend( self, scope, labels ):     # IF ( Expression ) Instruction | IF ( Expression ) Instruction ELSE Instruction
        if len( self ) == 5:
            pass
        else:
            pass

class LoopInstruction( Unit ): pass
class JumpInstruction( Unit ): pass

class DeclarationList( Unit ):
    def descend( self, scope ):     # Declaration | DeclarationList Declaration
        return self[ 0 ].descend( scope ) + ( self[ 1 ].descend( scope ) if len( self ) == 2 else [] )

class Declaration( Unit ):
    def descend( self, scope ):     # TypeName InitDeclaratorList ;
        self[ 0 ].descend( scope )
        return self[ 1 ].descend( scope, self[ 0 ].type )

class InitDeclaratorList( Unit ):
    def descend( self, scope, inherited_type ):     # InitDeclarator | InitDeclaratorList , InitDeclarator
        return self[ 0 ].descend( scope, inherited_type ) + ( self[ 1 ].descend( scope, inherited_type ) if len( self ) == 3 else [] )

class InitDeclarator( Unit ):
    def descend( self, scope, inherited_type ):     # DirectDeclarator | DirectDeclarator = Initializer
        lvalue = self[ 0 ].descend( scope, inherited_type )     # Will be None if declaring a function
        code = []
        if len( self ) == 3:
            code = self[ 2 ].descend( scope )

        return code

class DirectDeclarator( Unit ):
    def descend( self, scope, inherited_type ):     # IDN | IDN [ BROJ ] | IDN ( VOID ) | IDN ( ParameterList )
        if len( self ) == 1:                        # Defining an int or a char
            if scope.depth == 0:                    # Global variable
                label = FRISC.get_next_data_label()
                location = FRISC.get_next_data_location( inherited_type.size() )
                var = Variable( self[ 0 ].content, inherited_type, '({})'.format( label ) )
                scope[ var.name ] = var
                FRISC.place_data_in_memory( [ '\tORG {:X}'.format( location ), '\tDS {:X}'.format( inherited_type.size() ), '' ] )
                return var
            else:                                   # Local array
                var = Variable( self[ 0 ].content, inherited_type, '(R5+{:X})'.format( 4*scope.get_local_vars() ) )
                scope.make_local_var( 4 )
                scope[ var.name ] = var
                return var
        elif self[ 1 ].name == 'L_UGL_ZAGRADA':     # Defining an int or char array
            if scope.depth == 0:                    # Global array
                size = int( self[ 2 ].content )
                label = FRISC.get_next_data_label()
                location = FRISC.get_next_data_location( inherited_type.to_array().size( size ) )
                var = Variable( self[ 0 ].content, inherited_type.to_array(), '#'+label, size )
                scope[ var.name ] = var
                FRISC.place_data_in_memory( [ '\tORG {:X}'.format( location ), '\tDS {:X}'.format( var.type.size( var.array_size ) ), '' ] )
                return var
            else:                                   # Local array
                size = int( self[ 2 ].content )
                var = Variable( self[ 0 ].content, inherited_type.to_array(), '_R5+{:X}'.format( scope.get_local_vars() ), size )
                scope.make_local_var( inherited_type.to_array().size( size ) )
                scope[ var.name ] = var
                return var
        else:                                       # Function definition
            parameters = self[ 3 ].parameters if isinstance( self[ 3 ], ParameterList ) else []
            parameter_types = [ param.type for param in parameters ] if parameters else Void
            scope[ self[ 0 ].content ] = Function( self[ 0 ].content, FunctionType( inherited_type, parameter_types ) )

class Initializer( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.value = Value

    def descend( self, scope ):     # AssignmentExpression | { AssignmentExpressionList }
        if len( self ) == 1:
            self[ 0 ].descend( scope )
            self.value = self[ 0 ].value
        else:
            self[ 1 ].descend( scope )
            self.value = self[ 0 ].value

class ArgumentList( Unit ): pass

class AssignmentExpressionList( Unit ): pass
class Expression( AbstractExpression ): pass
class AssignmentExpression( AbstractExpression ): pass
class PostfixExpression( AbstractExpression ):
    def descend( self, scope ):     # PrimaryExpression | PostfixExpression [ Expression ] | PostfixExpression () | PostfixExpression ( ArgumentList ) | PostfixExpression ++ | PostfixExpression --
        if len( self ) == 1:
            self[ 0 ].descend( scope )
            self.value = self[ 0 ].value
            return []
        elif len( self ) == 2:
            self[ 0 ].descend( scope )
            if self[ 1 ].name == 'OP_INC':
                raise NotImplementedError
            else:
                raise NotImplementedError
        elif len( self ) == 3:
            self[ 0 ].descend( scope )


class PrimaryExpression( AbstractExpression ):
    def descend( self, scope ):     # IDN | BROJ | ZNAK | NIZ_ZNAKOVA | ( Expression )
        if len( self ) == 1:
            if self[ 0 ].name == 'IDN':     #
                self.result = scope[ self[ 0 ].content ]
            elif self[ 0 ].name == 'BROJ':  #
                self.result = Constant( int( self[ 0 ].content ), Int )
            elif self[ 0 ].name == 'ZNAK':
                self.result = Constant( int( self[ 0 ].content ), Char )
            else: raise NotImplementedError
        else:
            self.value = self[ 1 ].value

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
