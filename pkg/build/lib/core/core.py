"""
Defines `Core`.

Instantiates the module-level logger with the appropriate naming
convention.
"""

import logging
from abc import ABC

from interface.interface import Interface
from astparser.astparser import AstParser
from record.record import Record
from exception.exception import NoFilesSpecifiedError

LOGGER = logging.getLogger(__name__)


class Core(ABC):
    """
    Define the object responsible for the project's three main features.

    `Core` is also responsible for administrating the `Interface` and
    `AstParser` objects but mainly exists as a straightforward and
    moderated view inside the complex internal functionality of IDA-CFP.

    While the instances of `Interface` and `AstParser` can be explicitly
    accessed by other third-party code, this is not recommended as both
    objects contain no (strict) immutable state.
    """

    def __init__(self) -> None:
        """
        Initialize the `Core` object.

        Unlike the __init__ of `AstParser`, the internal state of _intr
        and _astp persists between files specified.

        `self._intr` contains an instance of the `Interface` object and
        is responsible for providing access to high level file I/O
        functionality.

        `self._astp` contains an instance of the `AstParser` object and
        is responsible for processing and understanding the abstract
        syntax tree (AST) that PycParser generates.

        :return: returns nothing
        """
        self._intr = Interface()
        self._astp = AstParser()

    def process_files(self, files: list) -> None:
        """
        Process a list of file I/O objects.

        For each file specified in the `files` list, its AST
        is loaded and properly processed before it is added
        to the module-level `Record`.

        :param files: list of argparser IO wrappers
        :return: returns nothing
        """
        # If the `files` list is found to be empty or improperly
        # populated then a `NoFileSpecifiedError` is raised
        if not files:
            raise NoFilesSpecifiedError()

        for f_str in files:
            ast = self._intr.load_new_ast(f_str.name)
            self._astp.process_ast(ast)

        # Rather than attempt to integrate the list and dict after
        # every file, it saves huge computational complexity to just
        # condense the operation and only do it once per run
        Record.integrate_list_to_dict()

    def generate_bundle(self) -> None:
        """
        Generate the bundle interface for disk I/O.

        Utilize the `Interface`-based conversion functionality to
        convert from the master `Record` dictionary of string: function
        pairs to a `json` string dump.

        :return: returns nothing
        """
        self._intr.convert_dict_to_json(Record.str_func_dict)

    def export(self) -> None:
        """
        Export the final bundle to disk.

        Utilize the `Interface`-based file-I/O system to drop the
        converted json string data to out/bundle.json.

        :return: returns nothing
        """
        self._intr.drop_bundle_to_disk(self._intr.json_data)
