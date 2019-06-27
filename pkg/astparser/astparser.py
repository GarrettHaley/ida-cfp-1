"""
Defines `AstParser`.

Instantiates the module-level logger with the appropriate naming
convention.
"""

import logging
from abc import ABC
import sys
from pycparser import c_ast

from verifier.verifier import Verifier
from record.record import Record
from exception.exception import AstEmptyError

LOGGER = logging.getLogger(__name__)


class AstParser(ABC):
    """
    Define the object responsible for navigating and processing ASTs.

    `AstParser` provides a traversal system interface compatible with
    a top-level AST or an arbitrary per-node `c_ast.NodeVisitor`.

    A fully parsed AST object averages between 30 and 50 bytes. Anything
    less than the `MIN_BYTES` class variable can be an indication of a
    more serious problem.
    """

    MIN_BYTES = 10

    def __init__(self) -> None:
        """
        Initialize the `AstParser` object.

        The internal state of the `ConstantVisitor` and `FuncDefVisitor`
        is not persisted between parsed files as __init__ is called.

        :return: returns nothing
        """
        self.const_visitor = ConstantVisitor()
        self.func_visitor = FuncDefVisitor()

    def process_ast(self, ast) -> None:
        """
        Process an AST by node using custom derived `Visitor`s.

        Properly processing and internalizing an AST for the purposes
        of discovering all unique strings, and which functions are
        responsible for handling those strings consists of two distinct
        parts: find the functions, find the strings within those
        functions.

        For the above process, this function serves only as the moderator.

        :param ast: top-level AST generated as a result of parse_file
        :return: returns nothing
        """
        # Unless the file is blank, there will always be a generated
        # AST. Any result otherwise is a critical error
        if sys.getsizeof(ast) < AstParser.MIN_BYTES:
            raise AstEmptyError()

        self.build_function_str_pairs(ast)

        # Opposite of the size check above, finding no strings within an
        # AST is perfectly reasonable, however it can be cause for concern
        if not Record.tpl_list:
            LOGGER.warning("No strings found in target file")

    def build_function_str_pairs(self, ast) -> None:
        """
        Construct a list of tuples of functions: strings for an AST.

        Before adding anything to the master `Record` list of tuples
        the entire AST has to be traversed and any `FuncDef` nodes
        captured. Then, iterating each node and recursively searching
        for constants (strings) results in a list of all strings used
        by that function.

        Every string, regardless of its status as unique is added to the
        list of tuples. Uniqueness only becomes a factor once all files
        have been parsed and its time to add things to the final
        dictionary.

        :param ast: top-level AST generated as a result of parse_file
        :return: returns nothing
        """
        function_list = self.locate_functions(ast)
        function_strings = []

        for function_node in function_list:

            # Explicitly clearing the list of strings using clear() is
            # unfortunately the most elegant way to ensure that no
            # strings from the last function_node persist to the second
            function_strings.clear()
            function_strings = self.locate_func_strings(function_node)

            for function_str in function_strings:
                Record.add_func_str_to_list(function_node.decl.name,
                                            function_str)

        # While dictionaries are not inherently sortable, they do preserve
        # their insertion order. Thus, keeping the list of tuples pre-sorted
        # ensures that the final dictionary is at least somewhat in order
        Record.sort_tmp_list()

        # Clear all of the nodes and values for the ConstantVisitor
        # and FuncDefVisitor instances
        self.__init__()

    def locate_functions(self, ast) -> list:
        """
        Locate all function definitions within an AST.

        Utilizes the `FuncDefVisitor`, which is derived from the
        `NodeVisitor` base class that is responsible for visiting c_ast
        nodes. Additional details can be found under the `FuncDefVisitor`
        class definition.

        :param ast: top-level AST generated as a result of parse_file
        :return self.func_visitor.nodes: list of all c_ast function nodes
        """
        # Calls the `NodeVisitor` base class' visit(), which constructs the
        # custom `FuncDef` visit() function
        self.func_visitor.visit(ast)

        # Log each function names
        Verifier.check_num_ast_functions(self.func_visitor.nodes)

        return self.func_visitor.nodes

    def locate_func_strings(self, node) -> list:
        """
        Locate all strings used within a function's definition.

        Searches, without diving (non-recursive) below, all of the constants
        found within a mini-AST or function node AST. Constants which are
        not strings are stripped by the `ConstantVisitor`.

        :param node: `FuncDef` node
        :return self.const_visitor.values: list of all strings a function uses
        """
        self.const_visitor.visit(node)
        return self.const_visitor.values


class ConstantVisitor(c_ast.NodeVisitor):
    """
    Define the object responsible for locating constants in ASTs.

    `ConstantVisitor` is the example derived `NodeVisitor` described
    in the PycParser documentation at L:109
    https://github.com/eliben/pycparser/blob/master/pycparser/c_ast.py
    """

    def __init__(self) -> None:
        """
        Initialize the `ConstantVisitor` object.

        :return: returns nothing
        """
        self.values = []

    def visit_Constant(self, node) -> None:
        """
        Create a list of values of the constant nodes encountered.

        Does not traverse the children of nodes for which this function
        was defined. To do that, call the base `NodeVisitor` member
        function generic_visit() on the target node.

        :param node: AST `FuncDef` node
        :return: returns nothing
        """
        try:
            # Ints are not captured as unique identifiers in IDA-CFP
            # and thus must be removed from the list of potential
            # unique constants
            int(node.value)

        except ValueError:
            # When strings are found by traversal they are wrapped in an
            # extra set of double quotes.
            stripped = node.value.replace('"', '')
            if stripped:
                self.values.append(stripped)


class FuncDefVisitor(c_ast.NodeVisitor):
    """
    Define the object responsible for locating function definitions in ASTs.

    `FuncDefVisitor` is the example derived `NodeVisitor` described
    in the PycParser documentation at L:25
    https://github.com/eliben/pycparser/blob/master/examples/func_defs.py
    """

    def __init__(self) -> None:
        """
        Initialize the `FuncDefVisitor` object.

        :return: returns nothing
        """
        self.nodes = []

    def visit_FuncDef(self, node) -> None:
        """
        Create a list of `FuncDef` nodes encountered.

        Does not traverse the children of nodes for which this function
        was defined. To do that, call the base `NodeVisitor` member
        function generic_visit() on the target node.

        :param node: top-level AST generated as a result of parse_file
        :return: returns nothing
        """
        self.nodes.append(node)
