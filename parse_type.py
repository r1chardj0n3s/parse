# -*- coding: utf-8 -*-
"""
Provides support to compose user-defined parse types.

Cardinality
------------

It is often useful to constrain how often a data type occurs.
This is also called the cardinality of a data type (in a context).
The supported cardinality are:

  * 0..1  zero_or_one,  optional<T>: T or None
  * 0..N  zero_or_more, list_of<T>
  * 1..N  one_or_more,  list_of<T> (many)

EXAMPLE:

    >>> from parse_type import TypeBuilder
    >>> from parse import Parser
    >>> def parse_number(text):
    ...     return int(text)
    >>> parse_number.pattern = r"\d+"
    >>> parse_many_numbers = TypeBuilder.with_many(parse_number)
    >>> more_types = { "Numbers": parse_many_numbers }
    >>> parser = Parser("List: {numbers:Numbers}", more_types)
    >>> parser.parse("List: 1, 2, 3")
    <Result () {'numbers': [1, 2, 3]}>


Enumeration Type (Name-to-Value Mappings)
-----------------------------------------

An Enumeration data type allows to select one of several enum values by using
its name. The converter function returns the selected enum value.

EXAMPLE:

    >>> from parse_type import TypeBuilder
    >>> from parse import Parser
    >>> parse_enum_yesno = TypeBuilder.make_enum({"yes": True, "no": False})
    >>> more_types = { "YesNo": parse_enum_yesno }
    >>> parser = Parser("Answer: {answer:YesNo}", more_types)
    >>> parser.parse("Answer: yes")
    <Result () {'answer': True}>


Choice (Name Enumerations)
-----------------------------

A Choice data type allows to select one of several strings.

EXAMPLE:

    >>> parse_choice_yesno = TypeBuilder.make_choice(["yes", "no"])
    >>> more_types = { "ChoiceYesNo": parse_choice_yesno }
    >>> parser = Parser("Answer: {answer:ChoiceYesNo}", more_types)
    >>> parser.parse("Answer: yes")
    <Result () {'answer': 'yes'}>

"""

from parse import TypeBuilder as TypeBuilderBase

class TypeBuilder(TypeBuilderBase):
    """
    Provides a utility class to build type-converters (parse_types) for parse.
    """
    default_pattern = r".+?"

    @staticmethod
    def make_enum(enum_mappings):
        """
        Create a type-converter function object for this enumeration.

        :param enum_mappings: Defines enumeration names and values.
        :return: Type-converter (parse_enum) function object.
        """
        def parse_enum(text):
            if text not in parse_enum.mappings:
                text = text.lower()     # REQUIRED-BY: parse re.IGNORECASE
            return parse_enum.mappings[text]    #< text.lower() ???
        parse_enum.pattern = r"|".join(enum_mappings.keys())
        parse_enum.mappings = enum_mappings
        return parse_enum

    @staticmethod
    def make_choice(choices, value_converter=None):
        """
        Creates a type-converter function to select one from a list of strings.
        The type-converter function returns the selected choice_text.

        :param choices: List of strings as choice.
        :param value_converter: Optional converter for selected string value.
        :return: Type-converter (parse_choice) function object.
        """
        assert value_converter is None or callable(value_converter)
        choices = list(choices)
        def parse_choice(text):
            assert text in parse_choice.choices
            # text = text.strip()
            if value_converter:
                return value_converter(text)
            return text
        parse_choice.pattern = r"|".join(choices)
        parse_choice.choices = choices
        return parse_choice

    @staticmethod
    def make_choice2(choices):
        """
        Creates a type-converter function to select one from a list of strings.
        The type-converter function returns a tuple (index, choice_text).

        :param choices: List of strings as choice.
        :param value_converter: Optional converter for selected string value.
        :return: Type-converter (parse_choice) function object.
        """
        choices = list(choices)
        def parse_choice2(text):
            assert text in parse_choice2.choices
            # text = text.strip()
            if not text:
                return None #< OPTIONAL CASE OCCURED.
            index = parse_choice2.choices.index(text)
            return index, text
        parse_choice2.pattern = r"|".join(choices)
        parse_choice2.choices = choices
        return parse_choice2

# -- IDEA:
#    @classmethod
#    def make_type_choice(cls, type_converters):
#        """
#        Creates a type-converter function for several converter alternatives.
#
#        :param type_converters: List of type-converter alternatives.
#        :return: Type-converter function object.
#        """
#        needs_default_pattern = 0
#        choice_patterns = []
#        for type_converter in type_converters:
#            pattern = getattr(type_converter, "pattern", None)
#            if not pattern:
#                needs_default_pattern += 1
#                continue
#            choice_patterns.append(pattern)
#        if needs_default_pattern:
#            assert needs_default_pattern == 1
#            choice_patterns.append(cls.default_pattern)
#
#        def parse_type_choice(text):
#            # NEED TO KNOW: Which type converter pattern was matched.
#            # return parse_type_choice.converters[x](text)
#            return text
#
#        parse_type_choice.pattern = r"|".join(choice_patterns)
#        parse_type_choice.converters = type_converters
#        return parse_type_choice

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# -----------------------------------------------------------------------------
# Copyright (c) 2012 by Jens Engel (https://github/jenisys/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
