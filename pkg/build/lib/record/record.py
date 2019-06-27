"""
Defines `Record`.

Instantiates the module-level logger with the appropriate naming
convention.
"""

import logging
import operator
from abc import ABC

from verifier.verifier import Verifier
from exception.exception import NoUniqueStringsError

LOGGER = logging.getLogger(__name__)


class Record(ABC):
    """
    Define the object responsible for maintaining state across modules.

    The two most important components of `Record` are the dictionary of
    unique strings and the functions which use them, along with the
    list of tuples which contains every string and function found in
    every AST.

    `Record` largely exists as a way to interact with specific state across
    six different independent modules. Granted, there are other ways of
    solving this problem however many of them require excessive parameter
    management and that wasn't something this project could support.

    Because this object is interfaced with on so many different levels, all
    of the methods are decorated as @classmethods.
    """

    # The str_func_dict is responsible for maintaining the master record
    # of all truly unique strings and the functions they are used within.
    # To be added to this dictionary candidancy must be first properly
    # adjudicated.

    # While dictionaries cannot be sorted, the list of tuples is sorted by
    # file and then alphabetically by string
    str_func_dict = {}

    # The tpl_list is a list of tuples containing all of the strings and
    # associated functions for a given C99 standard file. Regardless of
    # the content, uniqueness, or function-relevancy, all strings are
    # added. After a single file has finished its processing, this list is
    # returned to the below state.

    # Strings are paired with the functions they are used within using
    # tuples, like the following:
    # [("my_function", "myString"), ("func2", "str2")]
    tpl_list = []

    @classmethod
    def integrate_list_to_dict(cls) -> None:
        """
        Integrate the `Record` list of tuples into the `Record` dictionary.

        To prepare the list and associated tuples for addition into the 
        `Record` dictionary there are two steps that must be taken. The first
        is to remove all non-unique tuples from the list, this means all tuples
        that have a common string (function: string) between themselves and
        another tuple in the list. The second is to pre-sort the list by
        function name because dictionaries cannot be sorted, they can only
        preserved their insertion order.

        Following the completion of those two steps, the sorted list will
        contain only sorted tuples that are entirely unique. Then they can be
        added to the dictionary.

        :return: returns nothing
        """
        cls.remove_non_unique_from_list()
        cls.sort_tmp_list()
        cls.add_unique_to_dict()

    @classmethod
    def remove_non_unique_from_list(cls) -> None:
        """
        Remove tuples that share non-unique strings from the `Record` list.

        :return: returns nothing
        """
        strings = []
        to_remove = []

        for item in cls.tpl_list:

            # Capture only a list of the strings. Dealing with removal
            # of tuples based just the list of tuples itself quickly
            # becomes a nightmare
            strings.append(item[1])

        for string in strings:

            # Computationally speaking, this for and if statement are
            # O(n^2), which is less than ideal but necessary given the
            # constraints
            if strings.count(string) > 1:
                to_remove.append(string)

        for removal in to_remove:

            # There are other ways to remove tuples that match the second
            # element but those approaches are far more verbose than
            # the following list comprehension
            cls.tpl_list = [i for i in cls.tpl_list if i[1] != removal]

    @classmethod
    def sort_tmp_list(cls) -> None:
        """
        Sort the `Record` list by function name.

        :return: returns nothing
        """
        # Sort the list of tuples by the first element (function name),
        # in ascending order (the default of sort())
        cls.tpl_list.sort(key=operator.itemgetter(0))

    @classmethod
    def add_unique_to_dict(cls) -> None:
        """
        Add all unique function: string tuples to the `Record` dictionary.

        :return: returns nothing
        """
        reverse = [(t[1], t[0]) for t in cls.tpl_list]

        # Final confirmation that the list is not empty. If it is, then a
        # warning is generated through the module-level logger
        Verifier.check_list_dict_conversion(reverse)

        # Inserting new elements through update is far cleaner than
        # utilizing an index by key and setting each one individually
        cls.str_func_dict.update(dict(reverse))

        try:
            if not Verifier.check_num_dict_functions(cls.str_func_dict):
                raise NoUniqueStringsError()

        except NoUniqueStringsError:
            LOGGER.warning("No strings found in final dictionary")

    @classmethod
    def add_func_str_to_list(cls, new_func: str, new_string: str) -> None:
        """
        Add a new function: string tuple to the `Record` list.

        :param new_func: new function name to add
        :param new_string: new string constant to add
        :return: returns nothing
        """
        # Append to the end of the list. Order of tuples doesn't matter until
        # it comes time to insert unique tuples into the `Record` dictionary
        cls.tpl_list.append(tuple((new_func, new_string)))
