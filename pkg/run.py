"""
Defines main.

Instantiates the root-level logging instance, which is used throughout
the six distinct modules and broadly manages program flow.
"""

import argparse
import logging
import sys

from core.core import Core
from verifier.verifier import Verifier

# Logger instances are named according to their module __name__. This is
# true across each sub-module of the project.
LOGGER = logging.getLogger(__name__)


def main() -> int:
    """
    Define the project's mainline execution.

    Creates and interacts with the command line argument parser, `argparse`,
    in addition to setting the debugging standard project-wide, and initiating
    file processing with the `Core` module.

    This method exists largely as a pseudo-manager for keeping track of program
    flow and high-level return codes.
    """
    # Define a program for the argument argparser
    argparser = argparse.ArgumentParser(description="C file parser for unique \
        strings and their associated functions")

    # Verbosity is a boolean flag rather than the traditional level
    argparser.add_argument("-v", "--verbose", help="Set verbosity/\
        debug level", action="store_true")

    # A user may specify n files as positional arguments
    argparser.add_argument("files", type=argparse.FileType("r"), nargs="+")

    # Grab the arguments from the command line
    args = argparser.parse_args()

    # Configures the hierarchical (root-level) logger instance
    # TODO: Granularity beyond ON/OFF may follow in future releases
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Create an instance of `Core`, which is responsible for managing
    # high level functionality and program flow
    mngr = Core()

    # Double check that the files specified on the command line are
    # in the proper mode and exist at the correct location
    Verifier.check_parsable(args.files)

    # Process each file, appending unique func:str pairs as found
    mngr.process_files(args.files)

    # Ultimately produce a final dictionary and convert to JSON
    mngr.generate_bundle()

    # Drop the JSON bundle to disk under the out/ directory
    mngr.export()

    return 0

# Wrapping main within exit works effectively as a higher-order function
# allowing main to behave like a traditional system executable
if __name__ == '__main__':
    sys.exit(main())
