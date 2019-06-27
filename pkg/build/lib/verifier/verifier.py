"""
Defines `Verifier`.

Instantiates the module-level logger with the appropriate naming
convention.
"""

import logging
from abc import ABC
from pathlib import Path

from exception.exception import DirStatusError, \
    BundleCreationError, NoFunctionsFoundError, \
    FilePermissionsError, FileLocationError, \
    ListDictConversionError

LOGGER = logging.getLogger(__name__)


class Verifier(ABC):
    """
    Define the object responsible for performing checks on program state.

    `Verifier` exists entirely as a collection of utility functions defined
    as class static methods. Only in two different cases does the class
    have a return value other than None; checking the dictionary functions
    and comparing the list and dictionary.
    """

    @staticmethod
    def check_parsable(files: list) -> None:
        """
        Determine if a set of files have read permissions and name attributes.

        `Argparser` generates a list of file IO wrappers based on what files
        are specified on the command line, however the core attributes of
        each file object are not properly verified. For completeness's sake
        this function serves as a secondary check.

        If any of the two checks do pass, execution cannot continue under any
        circumstances.

        :param files: list of argparser IO wrappers
        :return: returns nothing
        """
        for file_io in files:

            # Files are only attempted to be opened as read only
            if file_io.mode != 'r':
                raise FilePermissionsError("File has no read permissions")

            # Argparser traditionally prefills the name field
            if not file_io.name:
                raise FileLocationError("File has no name property")

    @staticmethod
    def check_num_ast_functions(nodes) -> None:
        """
        Count the number of functions found within a set of nodes or full AST.

        Should a file be successfully pre-processed by clang and loaded as an
        AST but contain no functions, something went horribly wrong.

        :param nodes: list of function declaration nodes
        :return: returns nothing
        """
        count = 0

        for node in nodes:
            count = count + 1

            # Each function definition node (from c_ast.NodeVisitor) contains
            # specific properties, one of which being name. More info here at
            # https://docs.python.org/3/library/ast.html
            LOGGER.info('Function: %s', node.decl.name)

        if not count:
            raise NoFunctionsFoundError("No functions found in target file")

    @staticmethod
    def check_num_dict_functions(tmp_dict: dict) -> bool:
        """
        Checks the number of values stored in the dictionary.

        Largely utilized as a flag for issuing warnings when the final
        bundle is found to have no string: function pairs.

        :param tmp_dict: master dictionary of unique strings: functions
        :return bool(tmp_dict.values()): true if values exist, false otherwise
        """
        return bool(tmp_dict.values())

    @staticmethod
    def check_dict_by_list(tmp_list: list, tmp_dict: dict) -> list:
        """
        Locate common denominators between tuple list and dictionary keys.

        Before adding any tuple to the dictionary it is imperative that
        the dictionary does not already contain that key.

        :param tmp_list: list of tuples in the format (function, string)
        :param tmp_dict: master dictionary of unique strings: functions
        :return: list
        """
        to_remove = []

        for key in tmp_dict.keys():
            for pair in tmp_list:

                # Key must not already be in the list. If it is, appending
                # it will create a duplicate in the to_remove list
                if key == pair[1] and key not in to_remove:

                    # Add the second item in the tuple: (function, string)
                    to_remove.append(pair[1])

        return to_remove

    @staticmethod
    def check_list_dict_conversion(tmp_list: list) -> None:
        """
        Check if the list of tuples can be converted to a custom dictionary.

        Before swapping the tuples in the list and converting the unique
        strings to represent the keys in the dictionary, there must be at
        least one entry in the list.

        :param tmp_list: list of tuples
        :return: returns nothing
        """
        try:
            if not tmp_list:
                raise ListDictConversionError()

        except ListDictConversionError:
            LOGGER.warning("Empty list when converting to final dictionary")

    @staticmethod
    def check_bundle_creation(out_path_dir: str, out_path: str) -> None:
        """
        Test out/ directory and bundle file creation.

        :param out_path_dir: fully qualified path to the out/ directory
        :param out_path: fully qualified path to the json bundle
        :return: returns nothing
        """
        out_dir = Path(out_path_dir)
        out_file = Path(out_path)

        if not out_dir.is_dir():
            raise DirStatusError("Directory out/ is not valid")

        if not out_file.is_file():
            raise BundleCreationError("Bundle not created")
