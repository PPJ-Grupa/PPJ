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
        self.assigned = False

    def bool_evaluate( self ):     # Places 0 or 1 on top of stack
        code = self.result.place_on_stack()
        code += [ '\tPOP R0', '\tCMP R0, 0', '\tMOVE SR, R0', '\tAND R0, 8, R0', '\tXOR R0, 8, R0', '\tSHR R0, 3, R0', '\tPUSH R0' ]
        return code

class AbstractInstruction( Unit ): pass

################################################################################
# Semantic units                                                               #
################################################################################

# DONE
class CompilationUnit( Unit ):      pass  # ExternalDeclaration | CompilationUnit ExternalDeclaration

# DONE
class ExternalDeclaration( Unit ):        # FunctionDefinition | Declaration
    def descend( self, scope ):
        code = self[ 0 ].descend( scope )
        if code is not None:
            FRISC.place_code_in_global_scope( code )

# DONE
class FunctionDefinition( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.function = None
        self.parameters = []

    def descend( self, scope ): # TypeName IDN ( VOID | ParameterList ) ComplexInstruction
        self[ 0 ].descend( scope )
        self[ 3 ].descend( scope )
        self.parameters = self[ 3 ].parameters if isinstance( self[ 3 ], ParameterList ) else []
        parameter_types = [ param.type for param in self.parameters ] if self.parameters else Void

        self.function = Function( self[ 1 ].content, FunctionType( self[ 0 ].type, parameter_types ) )
        scope[ self[ 1 ].content ] = self.function
        if self.function.name == 'main': FRISC.register_main_function( self.function.label )

        local_scope = Scope( scope )
        for i, param in enumerate( reversed( self.parameters ) ):
            local_scope[ param.name ] = Variable( param.name, param.type, load_key = '(R5+0{:X})'.format( 4*( 2+i ) ) )

        labels = Labels( FRISC.get_next_generic_label( 'FEND' ) )

        child_code = self[ 5 ].descend( local_scope, labels )
        self.function.create_location( 24 + 4*len( child_code ) )

        code = [ ';=== Defining {} ===;'.format( self.function.name ) ]
        code += [ '\t`ORG 0{:X}'.format( self.function.location ), self.function.label, '\tPUSH R5', '\tMOVE SP, R5', '\tSUB SP, 0{:X}, SP'.format( local_scope.local_vars ) ]
        code += child_code
        code += [ labels.ret, '\tADD SP, 0{:X}, SP'.format( local_scope.local_vars ), '\tPOP R5', '\tRET', '' ]

        FRISC.place_function_in_memory( code )

# DONE
class ParameterList( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.parameters = []

    def descend( self, scope ):     # ParameterDeclaration | ParameterList , ParameterDeclaration
        super().descend( scope )
        self.parameters = ( [ self[ 0 ].parameter ] if len( self ) == 1 else
            ( self[ 0 ].parameters + [ self[ 2 ].parameter ] ) )

# DONE
class ParameterDeclaration( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.parameter = None

    def descend( self, scope ):
        super().descend( scope )    # TypeName IDN | TypeName IDN []
        self.parameter = FunctionParameter( self[ 1 ].content,
            ( self[ 0 ].type if len( self ) == 2 else self[ 0 ].type.to_array() ) )

# DONE
class ComplexInstruction( Unit ):
    def descend( self, scope, labels ):     # { InstructionList } | { DeclarationList InstructionList }
        local_scope = Scope( scope )
        if len( self ) == 3: return self[ 1 ].descend( local_scope, labels )
        return self[ 1 ].descend( local_scope ) + self[ 2 ].descend( local_scope, labels )

# DONE
class InstructionList( Unit ):
    def descend( self, scope, labels ):
        code = []
        for child in self.children:
            code += child.descend( scope, labels )
        return code

# DONE
class Instruction( Unit ):
    def descend( self, scope, labels ):
        return self[ 0 ].descend( scope, labels )

# DONE
class ExpressionInstruction( Unit ):
    def descend( self, scope, labels ):     # ; | Expression ;
        if len( self ) == 1: return []
        code = self[ 0 ].descend( scope )
        if not self[ 0 ].assigned: code += [ '\tPOP R0' ]
        return code
    def bool_evaluate( self ):
        return self[ 0 ].bool_evaluate() if len( self ) == 2 else []

# DONE
class BranchInstruction( Unit ):
    def descend( self, scope, labels ):     # IF ( Expression ) Instruction | IF ( Expression ) Instruction ELSE Instruction
        code = self[ 2 ].descend( scope )
        code += [ ';=== Start IF ===;' ]
        code += self[ 2 ].bool_evaluate()
        if len( self ) == 5:
            skip_label = FRISC.get_next_generic_label( 'SKIF' )
            code += [ '\tPOP R0', '\tCMP R0, 0', '\tJP_Z {}'.format( skip_label ) ]
            code += self[ 4 ].descend( scope, labels )
            code += [ skip_label ]
        else:
            else_label = FRISC.get_next_generic_label( 'ELSE' )
            end_label = FRISC.get_next_generic_label( 'NDIF' )
            code += [ '\tPOP R0', '\tCMP R0, 0', '\tJP_Z {}'.format( else_label ) ]
            code += self[ 4 ].descend( scope, labels )
            code += [ '\tJP {}'.format( end_label ), else_label ]
            code += self[ 6 ].descend( scope, labels )
            code += [ end_label ]
        code += [ ';=== End IF ===;' ]
        return code

# DONE
class LoopInstruction( Unit ):
    def descend( self, scope, labels ):     # WHILE ( Expression ) Instruction | FOR ( ExpressionInstruction ExpressionInstruction ) Instruction | FOR ( ExpressionInstruction ExpressionInstruction Expression ) Instruction
        if len( self ) == 5:                # While
            loop_label = FRISC.get_next_generic_label( 'WHIL' )
            end_label = FRISC.get_next_generic_label( 'NDWH' )
            labels.loop = loop_label
            labels.end_loop = end_label
            code = [ ';=== Start WHILE ===;' ]
            code += [ loop_label ]
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 0', '\tJP_Z {}'.format( end_label ) ]
            code += self[ 4 ].descend( scope, labels )
            code += [ '\tJP {}'.format( loop_label ), end_label, ';=== End WHILE ==;' ]
        elif len( self ) == 6:              # For ( EI EI ) I
            loop_label = FRISC.get_next_generic_label( 'FORL' )
            end_label = FRISC.get_next_generic_label( 'NDFR' )
            labels.loop = loop_label
            labels.end_loop = end_label
            code = [ ';=== Start FOR ===;' ]
            code += self[ 2 ].descend( scope, labels )
            code += [ loop_label ]
            code += self[ 3 ][ 0 ].descend( scope )
            code += self[ 3 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 0', '\tJP_Z {}'.format( end_label ) ]
            code += self[ 5 ].descend( scope, labels )
            code += [ '\tJP {}'.format( loop_label ), end_label, ';=== End FOR ===;' ]
        else:                               # For ( EI EI E ) I
            loop_label = FRISC.get_next_generic_label( 'FORL' )
            end_label = FRISC.get_next_generic_label( 'NDFR' )
            labels.loop = loop_label
            labels.end_loop = end_label
            code = [ ';=== Start FOR ===;' ]
            code += self[ 2 ].descend( scope, labels )
            code += [ loop_label ]
            code += self[ 3 ][ 0 ].descend( scope )
            code += self[ 3 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 0', '\tJP_Z {}'.format( end_label ) ]
            code += self[ 6 ].descend( scope, labels )
            code += self[ 4 ].descend( scope )
            if not self[ 4 ].assigned and isinstance( self[ 4 ].result, TopOfStack ):
                code += [ '\tPOP R0' ]
            code += [ '\tJP {}'.format( loop_label ), end_label, ';=== End FOR ===;' ]
        return code

# DONE
class JumpInstruction( Unit ):              # CONTINUE ; | BREAK ; | RETURN ; | RETURN Expression ;
    def descend( self, scope, labels ):
        if self[ 0 ].name == 'KR_CONTINUE':
            return [ '\tJP {}'.format( labels.loop ) ]
        elif self[ 0 ].name == 'KR_BREAK':
            return [ '\tJP {}'.format( labels.end_loop ) ]
        else:
            if len( self ) == 2:
                return [ '\tJP {}'.format( labels.ret ) ]
            else:
                code = self[ 1 ].descend( scope )
                code += self[ 1 ].result.place_on_stack()
                code += [ '\tPOP R6', '\tJP {}'.format( labels.ret ) ]
                return code

# DONE
class DeclarationList( Unit ):
    def descend( self, scope ):     # Declaration | DeclarationList Declaration
        return self[ 0 ].descend( scope ) + ( self[ 1 ].descend( scope ) if len( self ) == 2 else [] )

# DONE
class Declaration( Unit ):
    def descend( self, scope ):     # TypeName InitDeclaratorList ;
        self[ 0 ].descend( scope )
        code = self[ 1 ].descend( scope, self[ 0 ].type )
        return code

# DONE
class InitDeclaratorList( Unit ):
    def descend( self, scope, inherited_type ):     # InitDeclarator | InitDeclaratorList , InitDeclarator
        return self[ 0 ].descend( scope, inherited_type ) + ( self[ 1 ].descend( scope, inherited_type ) if len( self ) == 3 else [] )

# DONE
class InitDeclarator( Unit ):
    def descend( self, scope, inherited_type ):     # DirectDeclarator | DirectDeclarator = Initializer
        lvalue = self[ 0 ].descend( scope, inherited_type )     # Will be None if declaring a function
        code = []
        if len( self ) == 3:
            code = self[ 2 ].descend( scope )
            if self[ 2 ].is_list:
                code += [ ';=== List init ===;' ]
                for i in range( self[ 2 ].length ):
                    code += ArrayAccess( lvalue, Number( i ) ).store_from_stack()
            else:
                code += self[ 2 ].result.place_on_stack()
                code += lvalue.store_from_stack()
        return code

# DONE
class DirectDeclarator( Unit ):
    def descend( self, scope, inherited_type ):     # IDN | IDN [ BROJ ] | IDN ( VOID ) | IDN ( ParameterList )
        if len( self ) == 1:                        # Defining an int or a char
            if scope.depth == 0:                    # Global variable
                label = FRISC.get_next_data_label()
                location = FRISC.get_next_data_location( inherited_type.size() )
                var = Variable( self[ 0 ].content, inherited_type, '({})'.format( label ) )
                scope[ var.name ] = var
                FRISC.place_data_in_memory( [ '\t`ORG 0{:X}'.format( location ), label, '\t`DS 0{:X}'.format( inherited_type.size() ), '' ] )
                return var
            else:                                   # Local variable
                var = Variable( self[ 0 ].content, inherited_type, '(R5-0{:X})'.format( scope.get_local_vars() ) )
                scope.make_local_var( 4 )
                scope[ var.name ] = var
                return var
        elif self[ 1 ].name == 'L_UGL_ZAGRADA':     # Defining an int or char array
            if scope.depth == 0:                    # Global array
                size = int( self[ 2 ].content )
                label = FRISC.get_next_data_label()
                location = FRISC.get_next_data_location( inherited_type.to_array().size( size ) )
                var = Variable( self[ 0 ].content, inherited_type.to_array(), '#' + label, size )
                scope[ var.name ] = var
                FRISC.place_data_in_memory( [ '\t`ORG 0{:X}'.format( location ), label, '\t`DS 0{:X}'.format( var.type.size( var.array_size ) ), '' ] )
                return var
            else:                                   # Local array
                size = int( self[ 2 ].content )
                var = Variable( self[ 0 ].content, inherited_type.to_array(), '_R5-0{:X}'.format( scope.get_local_vars()+4*(size-1) ), size )
                scope.make_local_var( inherited_type.to_array().size( size ) )
                scope[ var.name ] = var
                return var
        else:                                       # Function definition
            parameters = self[ 3 ].parameters if isinstance( self[ 3 ], ParameterList ) else []
            parameter_types = [ param.type for param in parameters ] if parameters else Void
            scope[ self[ 0 ].content ] = Function( self[ 0 ].content, FunctionType( inherited_type, parameter_types ) )

# DONE
class Initializer( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.result = None
        self.is_list = None
        self.length = None

    def descend( self, scope ):     # AssignmentExpression | { AssignmentExpressionList }
        if len( self ) == 1:
            code = self[ 0 ].descend( scope )
            self.result = self[ 0 ].result
            self.is_list = False
        else:
            code = self[ 1 ].descend( scope )
            self.is_list = True
            self.length = self[ 1 ].length
        return code

# DONE
class ArgumentList( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.params = []

    def descend( self, scope ):     # AssignmentExpression | ArgumentList , AssignmentExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.params = [ self[ 0 ].result ]
        else:
            code += self[ 2 ].descend( scope )
            self.params = self[ 0 ].params + [ self[ 2 ].result ]
        return code

# DONE
class AssignmentExpressionList( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.length = 0

    def descend( self, scope ):     # AssignmentExpression | AssignmentExpressionList , AssignmentExpression
        if len( self ) == 1:
            code = self[ 0 ].descend( scope )
            code += self[ 0 ].result.place_on_stack()
            self.length = 1
        else:
            code = self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += self[ 0 ].descend( scope )
            self.length = self[ 0 ].length + 1
        return code

# DONE
class Expression( AbstractExpression ):
    def descend( self, scope ):     # AssignmentExpression | Expression , AssignmentExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
            self.assigned = self[ 0 ].assigned
        else:
            code += self[ 2 ].descend( scope )
            self.result = self[ 2 ].result
            self.assigned = self[ 2 ].assigned
        return code

# DONE
class AssignmentExpression( AbstractExpression ):
    def descend( self, scope ):     # LogicalOrExpression | PostfixExpression = AssignmentExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += self[ 0 ].result.store_from_stack()
            self.result = self[ 0 ].result
            self.assigned = True
        return code

# DONE
class PostfixExpression( AbstractExpression ):
    def descend( self, scope ):     # PrimaryExpression | PostfixExpression [ Expression ] | PostfixExpression () | PostfixExpression ( ArgumentList ) | PostfixExpression ++ | PostfixExpression --
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
            return code
        elif len( self ) == 2:
            instr = { 'OP_INC' : 'ADD', 'OP_DEC' : 'SUB' }[ self[ 1 ].name ]
            code += self[ 0 ].result.place_on_stack()
            code += [ '\tPOP R0', '\tPUSH R0', '\t{} R0, 1, R0'.format( instr ), '\tPUSH R0' ]
            code += self[ 0 ].result.store_from_stack()
            self.result = TopOfStack()
        elif len( self ) == 3:              # PostfixExpression ()
            self.result = self[ 0 ].result.get_result()
            code += self[ 0 ].result.call()
        else:
            code += self[ 2 ].descend( scope )
            if self[ 1 ].name == 'L_UGL_ZAGRADA':   # PostfixExpression [ Expression ]
                self.result = ArrayAccess( self[ 0 ].result, self[ 2 ].result )
            else:                           # PostfixExpression ( ArgumentList )
                self.result = self[ 0 ].result.get_result()
                code += self[ 0 ].result.call( self[ 2 ].params )
        return code

# DONE (!)
class PrimaryExpression( AbstractExpression ):
    def descend( self, scope ):     # IDN | BROJ | ZNAK | NIZ_ZNAKOVA | ( Expression )
        code = []
        if len( self ) == 1:
            if self[ 0 ].name == 'IDN':
                self.result = scope[ self[ 0 ].content ]
            elif self[ 0 ].name == 'BROJ':
                self.result = Constant( int( self[ 0 ].content ), Int )
            elif self[ 0 ].name == 'ZNAK':
                self.result = Constant( ord( self[ 0 ].content[ 1 ] ), Char )
            else: raise NotImplementedError
        else:
            code += self[ 1 ].descend( scope )
            self.result = self[ 1 ].result
        return code

# DONE
class LogicalOrExpression( AbstractExpression ):
    def descend( self, scope ):     # LogicalAndExpression | LogicalOrExpression || LogicalAndExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            label_true = FRISC.get_next_generic_label( 'ORTR' )
            label_end = FRISC.get_next_generic_label( 'NDOR' )
            code += self[ 0 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 1', '\tJP_EQ {}'.format( label_true ) ]
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 1', '\tJP_EQ {}'.format( label_true ) ]
            code += [ '\tMOVE 0, R0', '\tPUSH R0', '\tJP {}'.format( label_end ) ]
            code += [ label_true, '\tMOVE 1, R0', '\tPUSH R0', label_end ]
            self.result = TopOfStack()
        return code

# DONE
class LogicalAndExpression( AbstractExpression ):
    def descend( self, scope ):     # BinaryOrExpression | LogicalAndExpression && BinaryOrExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            label_false = FRISC.get_next_generic_label( 'ANDF' )
            label_end = FRISC.get_next_generic_label( 'NDAN' )
            code += self[ 0 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 0', '\tJP_EQ {}'.format( label_false ) ]
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].bool_evaluate()
            code += [ '\tPOP R0', '\tCMP R0, 1', '\tJP_EQ {}'.format( label_false ) ]
            code += [ '\tMOVE 1, R0', '\tPUSH R0', '\tJP {}'.format( label_end ) ]
            code += [ label_false, '\tMOVE 0, R0', '\tPUSH R0', label_end ]
            self.result = TopOfStack()
        return code

# DONE
class BinaryOrExpression( AbstractExpression ):
    def descend( self, scope ):     # BinaryXorExpression | BinaryOrExpression (|) BinaryXorExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1', '\tOR R2, R1, R0', '\tPUSH R0' ]
            self.result = TopOfStack()
        return code

# DONE
class BinaryXorExpression( AbstractExpression ):
    def descend( self, scope ):     # BinaryXorExpression | BinaryOrExpression ^ BinaryXorExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1', '\tXOR R2, R1, R0', '\tPUSH R0' ]
            self.result = TopOfStack()
        return code

# DONE
class BinaryAndExpression( AbstractExpression ):
    def descend( self, scope ):     # EqualityExpression | BinaryAndExpression ^ EqualityExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1', '\tAND R2, R1, R0', '\tPUSH R0' ]
            self.result = TopOfStack()
        return code

# DONE
class EqualityExpression( AbstractExpression ):
    def descend( self, scope ):     # RelationalExpression | EqualityExpression == RelationalExpression | EqualityExpression != RelationalExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += [ ';=== Begin EQU ===;' ]
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1' ]
            label1 = FRISC.get_next_generic_label( 'EQU1' )
            label2 = FRISC.get_next_generic_label( 'EQU2' )
            cond_code = { 'OP_EQ' : 'EQ', 'OP_NEQ' : 'NE' }[ self[ 1 ].name ]
            code += [ '\tCMP R1, R2', '\tJP_{} {}'.format( cond_code, label1 ), '\tMOVE 0, R0', '\tPUSH R0', '\tJP {}'.format( label2 ), label1, '\tMOVE 1, R0', '\tPUSH R0', label2 ]
            code += [ ';=== End EQU ===;' ]
            self.result = TopOfStack()
        return code

# DONE
class RelationalExpression( AbstractExpression ):
    def descend( self, scope ):     # AdditiveExpression | RelationalExpression ( < | > | <= | >= ) AdditiveExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += [ ';=== Begin REL ===;' ]
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1' ]
            label1 = FRISC.get_next_generic_label( 'CMP1' )
            label2 = FRISC.get_next_generic_label( 'CMP2' )
            cond_code = { 'OP_LT' : 'SLT', 'OP_GT' : 'SGT', 'OP_LTE' : 'SLE', 'OP_GTE' : 'SGE' }[ self[ 1 ].name ]
            code += [ '\tCMP R1, R2', '\tJP_{} {}'.format( cond_code, label1 ), '\tMOVE 0, R0', '\tPUSH R0', '\tJP {}'.format( label2 ), label1, '\tMOVE 1, R0', '\tPUSH R0', label2 ]
            code += [ ';=== End REL ===;' ]
            self.result = TopOfStack()
        return code

# DONE
class AdditiveExpression( AbstractExpression ):
    def descend( self, scope ):     # MultiplicativeExpression | AdditiveExpression ( + | - ) MultiplicativeExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1', '\tADD R1, R2, R0' if self[ 1 ].name == 'PLUS' else '\tSUB R1, R2, R0', '\tPUSH R0' ]
            self.result = TopOfStack()
        return code

# DONE
class MultiplicativeExpression( AbstractExpression ):
    def descend( self, scope ):     # CastExpression | MultiplicativeExpression ( * | / | % ) CastExpression
        code = self[ 0 ].descend( scope )
        if len( self ) == 1:
            self.result = self[ 0 ].result
        else:
            instr = { 'OP_PUTA' : 'MULTPL', 'OP_DIJELI' : 'DIVIDE', 'OP_MOD' : 'MODULO' }[ self[ 1 ].name ]
            code += self[ 0 ].result.place_on_stack()
            code += self[ 2 ].descend( scope )
            code += self[ 2 ].result.place_on_stack()
            code += [ '\tPOP R2', '\tPOP R1', '\tCALL {}'.format( instr ), '\tPUSH R6' ]
            self.result = TopOfStack()
        return code

# DONE
class CastExpression( AbstractExpression ):
    def descend( self, scope ):     # UnaryExpression | ( TypeName ) CastExpression
        if len( self ) == 1:
            code = self[ 0 ].descend( scope )
            self.result = self[ 0 ].result
        else:
            code = self[ 3 ].descend( scope )
            self.result = self[ 3 ].result
        return code

# DONE
class UnaryExpression( AbstractExpression ):
    def descend( self, scope ):     # PostfixExpression | ( ++ | -- ) UnaryExpression | UnaryOperator CastExpression
        if len( self ) == 1:
            code = self[ 0 ].descend( scope )
            self.result = self[ 0 ].result
            return code
        elif isinstance( self[ 0 ], UnaryOperator ):
            self[ 0 ].descend( scope )
            op = self[ 0 ].operator
            code = self[ 1 ].descend( scope )
            code += self[ 1 ].result.place_on_stack()
            if op == '+':
                pass
            elif op == '-':
                code += [ '\tPOP R0', '\tXOR R0, -1, R0', '\tADD R0, 1, R0', '\tPUSH R0' ]
            elif op == '~':
                code += [ '\tPOP R0', '\tXOR R0, -1, R0', '\tPUSH R0' ]
            else:     # !
                pass
            self.result = TopOfStack()
            return code
        else:   # ++ | --
            instr = { 'OP_INC' : 'ADD', 'OP_DEC' : 'SUB' }[ self[ 0 ].name ]
            code = self[ 1 ].descend( scope )
            code += self[ 1 ].result.place_on_stack()
            code += [ '\tPOP R0', '\t{} R0, 1, R0'.format( instr ), '\tPUSH R0', '\tPUSH R0' ]
            code += self[ 1 ].result.store_from_stack()
            self.result = TopOfStack()
            return code

# DONE
class UnaryOperator( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.operation = None

    def descend( self, scope ):
        self.operator = { 'PLUS' : '+', 'MINUS' : '-', 'OP_TILDA' : '~', 'OP_NEG' : '!' }[ self[ 0 ].name ]

# DONE
class TypeName( Unit ):
    def __init__( self, depth ):
        super().__init__( depth )
        self.type = Undefined
    def descend( self, scope ): # TypeSpecifier | CONST TypeSpecifier
        super().descend( scope )
        self.type = self[ 0 ].type if len( self ) == 1 else self[ 1 ].type

# DONE
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
