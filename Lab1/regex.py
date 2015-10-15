from abc import ABCMeta, abstractmethod

from utils import tail


class Regex:
    """A custom regex implementation via an e-NKA finite state machine.

    After initialization, `self.machine` contains a pair ( start_node, end_node )
    of a FSM represented as a directed graph.

    The main functionality of the class is the `match` method which attempts to
    match a compiled pattern to the input string."""

    def __init__( self, pattern ):
        self.machine = Regex.build_state_machine( Regex.pattern_to_postfix( pattern ) )

    def match( self, input_string ):
        """Tries to match the input string to the precompiled pattern.

        If some prefix of the input satisfies the pattern, the method returns
        that prefix together with the remains of input, in a pair.
        If no prefix satisfies the pattern, a pair (None, input) is returned instead.

        The matching is greedy."""
        states = self.machine[ 0 ].epsilon_surrounding()
        last_match_index = -1
        for i, input_char in enumerate( input_string ):
            states = Node.set_epsilon_surrounding( Node.set_advance( states, input_char ) )
            if not states: break
            elif self.machine[ 1 ] in states: last_match_index = i

        return ( ( input_string[ :last_match_index+1 ], input_string[ last_match_index+1: ] )
                if last_match_index >= 0 else ( None, input_string ) )

    @staticmethod
    def pattern_to_postfix( pattern ):
        operator_stack = []
        postfix_pattern = []
        symbols = []
        preprocessed_symbols = []
        slash_precedeed = False
        for char in pattern:
            if slash_precedeed:
                symbols.append( Symbol( char, False ) )
                slash_precedeed = False
            elif char == '\\':
                slash_precedeed = True
            else:
                symbols.append( Symbol( char, Regex._is_special( char ) ) )
                slash_precedeed = False

        for i in range( 0, len( symbols ) ):
            if i > 0 and Regex._should_insert_concatenation( symbols[ i-1 ], symbols[ i ] ):
                preprocessed_symbols.append( Symbol( '.', True ) )
            preprocessed_symbols.append( symbols[ i ] )
        preprocessed_symbols = [ Symbol( '(', True ) ] + preprocessed_symbols + [ Symbol( ')', True ) ]

        for sym in preprocessed_symbols:
            if sym.special:
                if sym.char == '(':
                    operator_stack.append( sym )
                elif sym.char == ')':
                    while operator_stack[ -1 ].char != '(':
                        postfix_pattern.append( operator_stack.pop() )
                    operator_stack.pop()
                elif sym.char == '*':
                    postfix_pattern.append( sym )
                else:
                    while operator_stack and sym.get_priority() < operator_stack[ -1 ].get_priority():
                        postfix_pattern.append( operator_stack.pop() )
                    operator_stack.append( sym )
            else:
                postfix_pattern.append( sym )

        return postfix_pattern

    @staticmethod
    def build_state_machine( postfix_pattern ):
        operand_stack = []

        for sym in postfix_pattern:
            if not sym.special:
                operand_stack.append( sym )
            elif sym.char == '*':
                operand_stack.append( Kleene( operand_stack.pop() ) )
            elif sym.char == '.':
                operand_stack.append( Concat( operand_stack.pop(), operand_stack.pop() ) )
            elif sym.char == '|':
                operand_stack.append( Or( operand_stack.pop(), operand_stack.pop() ) )

        tree = operand_stack[ 0 ]

        return tree.build()

    @staticmethod
    def _is_special( char ):
        return char in ( '*', '|', '(', ')' )

    @staticmethod
    def _should_insert_concatenation( left_symbol, right_symbol ):
        return (  ( not left_symbol.special and not right_symbol.special )
               or ( not left_symbol.special and right_symbol.char == '(' )
               or ( left_symbol.char in ( ')', '*' ) and not right_symbol.special )
               or ( left_symbol.char == ')' and right_symbol.char == '(' ) )


class Buildable:
    @abstractmethod
    def build( self, string ):
        """Builds a finite-state machine, returns the initial and the terminal node"""
        pass


class Symbol( Buildable ):
    """A regex symbol, either an ordinary character or a special one"""
    def __init__( self, char, special ):
        self.char = char
        self.special = special

    def __repr__( self ):
        return '<{}>'.format( self.char ) if self.special else self.char

    def get_priority( self ):
        return { '.' : 1, '|' : 0, '(' : -1 }[ self.char ]

    def build( self ):
        end = Node()
        start = Node( ( end, self.char ) )
        return start, end


class Concat( Buildable ):
    """A regex concatenation (.) operator"""
    def __init__( self, second, first ):
        self.first = first
        self.second = second

    def __repr__( self ):
        return '<Concat {}, {}>'.format( self.first, self.second )

    def build( self ):
        first_start, first_end = self.first.build()
        second_start, second_end = self.second.build()
        start = Node( ( first_start, '$' ) )
        end = Node()
        first_end.add_link( ( second_start, '$' ) )
        second_end.add_link( ( end, '$' ) )
        return start, end


class Kleene( Buildable ):
    """A regex Kleene star (*) operator"""
    def __init__( self, item ):
        self.item = item

    def __repr__( self ):
        return '<Kleene {}>'.format( self.item )

    def build( self ):
        item_start, item_end = self.item.build()
        start = Node( ( item_start, '$' ) )
        end = Node( ( start, '$' ) )
        start.add_link( ( end, '$' ) )
        item_end.add_link( ( end, '$' ) )
        return start, end

class Or( Buildable ):
    """A regex or operator (|)"""
    def __init__( self, right, left ):
        self.left = left
        self.right = right

    def __repr__( self ):
        return '<Or {}, {}>'.format( self.left, self.right )

    def build( self ):
        left_start, left_end = self.left.build()
        right_start, right_end = self.right.build()
        start = Node( ( left_start, '$' ), ( right_start, '$' ) )
        end = Node()
        left_end.add_link( ( end, '$' ) )
        right_end.add_link( ( end, '$' ) )
        return start, end


class Node:
    """A finite-state machine node"""
    node_index = 0
    def __init__( self, *args ):
        self.links = list( args )
        self.index = Node.node_index
        Node.node_index += 1

    def add_link( self, link ):
        self.links.append( link )

    def __repr__( self ):
        return 'Node {}'.format( self.index )

    def epsilon_surrounding( self ):
        surrounding = set()
        stack = [ self ]
        while stack:
            node = stack.pop()
            surrounding.add( node )
            for link_node, link_char in node.links:
                if link_char == '$' and link_node not in surrounding:
                    stack.append( link_node )
        return surrounding

    def advance( self, char ):
        next_nodes = set()
        for link_node, link_char in self.links:
            if link_char == char:
                next_nodes.add( link_node )
        return next_nodes

    @staticmethod
    def set_epsilon_surrounding( node_set ):
        """Calculate the epsilon surrounding of a set of nodes"""
        surrounding = set()
        for node in node_set:
            surrounding |= node.epsilon_surrounding()
        return surrounding

    @staticmethod
    def set_advance( node_set, char ):
        """Advance a set of nodes by all `char` transitions"""
        next_nodes = set()
        for node in node_set:
            next_nodes |= node.advance( char )
        return next_nodes
