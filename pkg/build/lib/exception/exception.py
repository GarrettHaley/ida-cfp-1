"""
Defines `CustomBaseError` and derived errors.

Instantiates the module-level logger with the appropriate naming
convention.
"""

import logging

LOGGER = logging.getLogger(__name__)


class CustomBaseError(Exception):
    """
    Define the base exception type for IDA-CFP errors.

    `CustomBaseError` exists as the middleman between the Python v3
    `Exception` and each of the custom IDA-CFP specific errors.
    """


class FileLocationError(CustomBaseError):
    """Raised in the event a file has no name property."""

    def __init__(self, message) -> None:
        """
        Initialize, call base constructor and log critical message.

        :param message: custom exception message to alert and log
        :return: returns nothing
        """
        # Call the super class constructor with the parameters it requires
        super(FileLocationError, self).__init__(message)

        LOGGER.critical(message)


class NoFilesSpecifiedError(CustomBaseError):
    """Raised in the event files are incorrectly parsed by argparse."""


class NoneFilePathError(CustomBaseError):
    """Raised in the event a file's path is not fully qualified."""

    def __init__(self, message) -> None:
        """
        Initialize, call base constructor and log critical message.

        :param message: custom exception message to alert and log
        :return: returns nothing
        """
        # Call the super class constructor with the parameters it requires
        super(NoneFilePathError, self).__init__(message)

        LOGGER.critical(message)


class FilePermissionsError(CustomBaseError):
    """Raised in the event a file object does not have read permissions."""

    def __init__(self, message) -> None:
        """
        Initialize, call base constructor and log critical message.

        :param message: custom exception message to alert and log
        :return: returns nothing
        """
        # Call the super class constructor with the parameters it requires
        super(FilePermissionsError, self).__init__(message)

        LOGGER.critical(message)


class AstEmptyError(CustomBaseError):
    """Raised in the event an AST is less than the minimum required bytes."""


class NoFunctionsFoundError(CustomBaseError):
    """Raised in the event no functions are found within the target file."""

    def __init__(self, message) -> None:
        """
        Initialize, call base constructor and log critical message.

        :param message: custom exception message to alert and log
        :return: returns nothing
        """
        # Call the super class constructor with the parameters it requires
        super(NoFunctionsFoundError, self).__init__(message)

        LOGGER.critical(message)


class NoUniqueStringsError(CustomBaseError):
    """Raised in the event that the final dictionary contains no pairs."""


class ListDictConversionError(CustomBaseError):
    """Raised in the event the `Record` list cannot be converted to dict."""


class DirStatusError(CustomBaseError):
    """Raised in the event out/ is not a valid directory."""

    def __init__(self, message) -> None:
        """
        Initialize, call base constructor and log critical message.

        :param message: custom exception message to alert and log
        :return: returns nothing
        """
        # Call the super class constructor with the parameters it requires
        super(DirStatusError, self).__init__(message)

        LOGGER.critical(message)


class BundleCreationError(CustomBaseError):
    """Raised in the event the bundle is not properly dropped to disk."""

    def __init__(self, message) -> None:
        """
        Initialize, call base constructor and log critical message.

        :param message: custom exception message to alert and log
        :return: returns nothing
        """
        # Call the super class constructor with the parameters it requires
        super(BundleCreationError, self).__init__(message)

        LOGGER.critical(message)
