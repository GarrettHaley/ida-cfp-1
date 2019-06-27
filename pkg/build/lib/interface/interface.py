"""
Defines `Interface`.

Instantiates the module-level logger with the appropriate naming
convention.
"""

import logging
import json
import os
import platform
from abc import ABC
from pycparser import c_ast, parse_file

from verifier.verifier import Verifier
from exception.exception import NoneFilePathError

LOGGER = logging.getLogger(__name__)


class Interface(ABC):
    """
    Define the object responsible for file I/O and `json` interaction.

    `OUT_FILE` is the file name of the final "bundle" that is ultimately
    dropped to disk under the out/ directory. If that file name needs to
    be changed programmatically, this is the place to do it.

    `OUT_DIR` is the directory in which the `OUT_FILE` is placed. This
    class-variable exists as a convienient way for `Verifier` to test
    directory structure validity.

    `OUT_FILE_PATH` is the fully qualified path to the "bundle".
    """

    OUT_FILE = "bundle.json"
    OUT_DIR = os.getcwd() + "/out/"
    OUT_FILE_PATH = os.getcwd() + "/out/" + OUT_FILE

    def __init__(self) -> None:
        """
        Initialize the `Interface` object.

        `self.ast` contains the current AST for whichever file is
        being processed at the time. On each subsequent file load,
        the `self.ast` member variable is reset.

        `self.json_data` contains the "pretty-formatted" json string
        data that is eventually written to disk.

        :return: returns nothing
        """
        self.ast = None
        self.json_data = None

    def load_new_ast(self, file_path: str = "") -> c_ast.FileAST:
        """
        Load a new abstract syntax tree (AST).

        Check file path validity before selecting which type of clang
        executable to use for PycParser's `parse_file`.

        :param file_path: file to be parsed
        :return self.ast: PycParser AST
        """
        # PycParser requires a fully-qualified and valid file path
        # for any file to be properly parsed, therfore if a None-type
        # is encountered, immediately except
        if not file_path:
            raise NoneFilePathError("File path is not fully qualified")

        # While the requirements of the project list LLVM and associated
        # developer packages, these are sometimes differences between
        # clang file extensions of Windows vs. Unix
        clang_path = "clang"
        if platform.system() == "Windows":
            clang_path = "clang.exe"

        # Files of any size are supported, with the limits of execution
        # falling only on available user hardware. 50 megabytes of C
        # code in one file is a good place to draw the line
        size_mb = os.path.getsize(file_path) >> 20
        if size_mb > 50:
            LOGGER.warning("File size exceeds 50MB")

        # PycParser offers a few different ways to generate ASTs but the
        # following is by far the most clean. Clang is well developed
        # as a c pre-processor and installed by default on OS X
        self.ast = parse_file(file_path,
                              use_cpp=True,
                              cpp_path=clang_path,
                              cpp_args=['-E', '-Iutils/fake_libc_include'])

        return self.ast

    def convert_dict_to_json(self, data: dict) -> None:
        """
        Convert dictionary to `json`-pretty-formatted string.

        :param data: Master `Record` dictionary of string: function
        :return: returns nothing
        """
        # Call to dumps returns a sorted, and indented string, instead
        # of the json object more common usage of dump. In this case,
        # dumps needed to be used so any special escape slashes can
        # be properly stripped
        self.json_data = json.dumps(data, indent=4, sort_keys=True)

        # Quick reformat of the member variable `json_data` to remove
        # all "\\" and replace with "\"
        self.process_out_data()

        # If the conversion comes back with nothing or just {}, that is
        # cause for notification but not error or warning. Some files
        # will result in no unique strings being found
        if not self.json_data:
            LOGGER.warning("Empty bundle")

    def process_out_data(self) -> None:
        """
        Strip string of double backslashes and replace with single.

        Any double backslashes that were previously used to escape
        special characters need to be completely stripped. If not,
        the bundle dict keys will not contain the exact representation
        of the strings that exist in the target file.

        :return: returns nothing
        """
        self.json_data = self.json_data.replace("\\\\", "\\")

    def drop_bundle_to_disk(self, data) -> None:
        """
        Write dictionary as json string to out/ directory.

        :return: returns nothing
        """
        # Opening files using "w" truncates existing content or creates
        # a new file if it doesn't already exist. Save the old file
        # somewhere else or under a different name if persistence
        # between program runs is important
        with open(self.OUT_FILE_PATH, "w") as outfile:
            outfile.write(data)

        # Perform several checks on the validity of both out/ and on
        # the bundle itself
        Verifier.check_bundle_creation(self.OUT_DIR, self.OUT_FILE_PATH)
