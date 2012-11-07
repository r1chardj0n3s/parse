#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite  for parse_type.py

REQUIRES:
    parse >= 1.5.3.1 ('pattern' attribute support)
"""

import unittest
import parse
from parse_type import TypeBuilder

# -----------------------------------------------------------------------------
# TEST SUPPORT FOR: TypeBuilder Tests
# -----------------------------------------------------------------------------
# -- PROOF-OF-CONCEPT DATATYPE:
def parse_number(text):
    return int(text)
parse_number.pattern = r"\d+"   # Provide better regexp pattern than default.
parse_number.name = "Number"    # For testing only.

# -- ENUM DATATYPE:
parse_yesno = TypeBuilder.make_enum({
    "yes":  True,   "no":  False,
    "on":   True,   "off": False,
    "true": True,   "false": False,
})
parse_yesno.name = "YesNo"      # For testing only.

# -- ENUM DATATYPE:
parse_person_choice = TypeBuilder.make_choice(["Alice", "Bob", "Charly"])
parse_person_choice.name = "PersonChoice"      # For testing only.

# -----------------------------------------------------------------------------
# TEST CASE: TestTypeBuilder
# -----------------------------------------------------------------------------
class TestTypeBuilder(unittest.TestCase):

    # -- PYTHON VERSION BACKWARD-COMPATIBILTY:
    if not hasattr(unittest.TestCase, "assertIsNone"):
        def assertIsNone(self, obj, msg=None):
            self.assert_(obj is None, msg)

        def assertIsNotNone(self, obj, msg=None):
            self.assert_(obj is not None, msg)

    @staticmethod
    def build_type_dict(type_converters):
        """
        Builds type dictionary for user-defined type converters, used by parse.
        :param type_converters: List of type-converters (parse_types)
        :return: Type-converter dictionary
        """
        more_types = {}
        for type_converter in type_converters:
            more_types[type_converter.name] = type_converter
        return more_types

    def assert_match(self, parser, text, param_name, expected):
        """
        Check that a parser can parse the provided text and extracts the
        expected value for a parameter.

        :param parser: Parser to use
        :param text:   Text to parse
        :param param_name: Name of parameter
        :param expected:   Expected value of parameter.
        :raise: AssertationError on failures.
        """
        result = parser.parse(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[param_name], expected)

    def assert_mismatch(self, parser, text, param_name):
        """
        Check that a parser cannot extract the parameter from the provided text.
        A parse mismatch has occured.

        :param parser: Parser to use
        :param text:   Text to parse
        :param param_name: Name of parameter
        :raise: AssertationError on failures.
        """
        result = parser.parse(text)
        self.assertIsNone(result)


# -----------------------------------------------------------------------------
# TEST CASE: TestTypeBuilder4Cardinality
# -----------------------------------------------------------------------------
class TestTypeBuilder4Cardinality(TestTypeBuilder):

    def test_with_zero_or_one_basics(self):
        parse_opt_number = TypeBuilder.with_zero_or_one(parse_number)
        self.assertEqual(parse_opt_number.pattern, r"(\d+)?")

    def test_with_zero_or_one(self):
        parse_opt_number = TypeBuilder.with_zero_or_one(parse_number)
        parse_opt_number.name = "OptionalNumber"

        extra_types = self.build_type_dict([ parse_opt_number ])
        format_ = "Optional: {number:OptionalNumber}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "Optional: ",   "number", None)
        self.assert_match(parser, "Optional: 1",  "number", 1)
        self.assert_match(parser, "Optional: 42", "number", 42)

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: x",   "number")  # Not a Number.
        self.assert_mismatch(parser, "List: -1",  "number")  # Negative.
        self.assert_mismatch(parser, "List: a, b", "number") # List of ...

    def test_with_optional(self):
        # -- ALIAS FOR: zero_or_one
        parse_opt_number = TypeBuilder.with_optional(parse_number)
        parse_opt_number.name = "OptionalNumber"

        extra_types = self.build_type_dict([ parse_opt_number ])
        format_ = "Optional: {number:OptionalNumber}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "Optional: ",   "number", None)
        self.assert_match(parser, "Optional: 1",  "number", 1)
        self.assert_match(parser, "Optional: 42", "number", 42)

    def test_with_zero_or_more_basics(self):
        parse_numbers = TypeBuilder.with_zero_or_more(parse_number)
        self.assertEqual(parse_numbers.pattern, r"(\d+)?(\s*,\s*(\d+))*")

    def test_with_zero_or_more(self):
        parse_numbers = TypeBuilder.with_zero_or_more(parse_number)
        parse_numbers.name = "Numbers0"

        extra_types = self.build_type_dict([ parse_numbers ])
        format_ = "List: {numbers:Numbers0}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: ",        "numbers", [ ])
        self.assert_match(parser, "List: 1",       "numbers", [ 1 ])
        self.assert_match(parser, "List: 1, 2",    "numbers", [ 1, 2 ])
        self.assert_match(parser, "List: 1, 2, 3", "numbers", [ 1, 2, 3 ])

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: x",  "numbers")  # Not a Number.
        self.assert_mismatch(parser, "List: -1", "numbers")  # Negative.
        self.assert_mismatch(parser, "List: 1,", "numbers")  # Trailing sep.
        self.assert_mismatch(parser, "List: a, b", "numbers") # List of ...

    def test_with_zero_or_more_choice(self):
        parse_color  = TypeBuilder.make_choice(["red", "green", "blue"])
        parse_colors = TypeBuilder.with_zero_or_more(parse_color)
        parse_colors.name = "Colors0"

        extra_types = self.build_type_dict([ parse_colors ])
        format_ = "List: {colors:Colors0}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: ",           "colors", [ ])
        self.assert_match(parser, "List: green",      "colors", [ "green" ])
        self.assert_match(parser, "List: red, green", "colors", [ "red", "green" ])

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: x",  "colors")  # Not a Color.
        self.assert_mismatch(parser, "List: black", "colors")  # Unknown
        self.assert_mismatch(parser, "List: red,",  "colors")  # Trailing sep.
        self.assert_mismatch(parser, "List: a, b",  "colors")  # List of ...

    def test_with_one_or_more_basics(self):
        parse_numbers = TypeBuilder.with_one_or_more(parse_number)
        self.assertEqual(parse_numbers.pattern, r"(\d+)(\s*,\s*(\d+))*")

    def test_with_one_or_more_basics_with_other_separator(self):
        listsep = ';'
        parse_numbers2 = TypeBuilder.with_one_or_more(parse_number, listsep)
        self.assertEqual(parse_numbers2.pattern, r"(\d+)(\s*;\s*(\d+))*")

        listsep = ':'
        parse_numbers2 = TypeBuilder.with_one_or_more(parse_number, listsep)
        self.assertEqual(parse_numbers2.pattern, r"(\d+)(\s*:\s*(\d+))*")

    def test_with_one_or_more(self):
        parse_numbers = TypeBuilder.with_one_or_more(parse_number)
        parse_numbers.name = "Numbers"

        extra_types = self.build_type_dict([ parse_numbers ])
        format_ = "List: {numbers:Numbers}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: 1",       "numbers", [ 1 ])
        self.assert_match(parser, "List: 1, 2",    "numbers", [ 1, 2 ])
        self.assert_match(parser, "List: 1, 2, 3", "numbers", [ 1, 2, 3 ])

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: ",   "numbers")  # Zero items.
        self.assert_mismatch(parser, "List: x",  "numbers")  # Not a Number.
        self.assert_mismatch(parser, "List: -1", "numbers")  # Negative.
        self.assert_mismatch(parser, "List: 1,", "numbers")  # Trailing sep.
        self.assert_mismatch(parser, "List: a, b", "numbers") # List of ...

    def test_with_many(self):
        # -- ALIAS FOR: one_or_more
        parse_numbers = TypeBuilder.with_many(parse_number)
        parse_numbers.name = "Numbers"

        extra_types = self.build_type_dict([ parse_numbers ])
        format_ = "List: {numbers:Numbers}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: 1",       "numbers", [ 1 ])
        self.assert_match(parser, "List: 1, 2",    "numbers", [ 1, 2 ])
        self.assert_match(parser, "List: 1, 2, 3", "numbers", [ 1, 2, 3 ])

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: ",   "numbers")  # Zero items.

    def test_with_one_or_more_choice(self):
        parse_color  = TypeBuilder.make_choice(["red", "green", "blue"])
        parse_colors = TypeBuilder.with_one_or_more(parse_color)
        parse_colors.name = "Colors"

        extra_types = self.build_type_dict([ parse_colors ])
        format_ = "List: {colors:Colors}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: green",      "colors", [ "green" ])
        self.assert_match(parser, "List: red, green", "colors", [ "red", "green" ])

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: ",   "colors")  # Zero items.
        self.assert_mismatch(parser, "List: x",  "colors")  # Not a Color.
        self.assert_mismatch(parser, "List: black", "colors")  # Unknown
        self.assert_mismatch(parser, "List: red,",  "colors")  # Trailing sep.
        self.assert_mismatch(parser, "List: a, b",  "colors")  # List of ...

    def test_with_one_or_more_enum(self):
        parse_color  = TypeBuilder.make_enum({"red": 1, "green":2, "blue": 3})
        parse_colors = TypeBuilder.with_one_or_more(parse_color)
        parse_colors.name = "Colors"

        extra_types = self.build_type_dict([ parse_colors ])
        format_ = "List: {colors:Colors}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: green",      "colors", [ 2 ])
        self.assert_match(parser, "List: red, green", "colors", [ 1, 2 ])

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "List: ",   "colors")  # Zero items.
        self.assert_mismatch(parser, "List: x",  "colors")  # Not a Color.
        self.assert_mismatch(parser, "List: black", "colors")  # Unknown
        self.assert_mismatch(parser, "List: red,",  "colors")  # Trailing sep.
        self.assert_mismatch(parser, "List: a, b",  "colors")  # List of ...

    def test_with_one_or_more_with_other_separator(self):
        listsep = ';'
        parse_numbers2 = TypeBuilder.with_one_or_more(parse_number, listsep)
        parse_numbers2.name = "Numbers2"

        extra_types = self.build_type_dict([ parse_numbers2 ])
        format_ = "List: {numbers:Numbers2}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "List: 1",       "numbers", [ 1 ])
        self.assert_match(parser, "List: 1; 2",    "numbers", [ 1, 2 ])
        self.assert_match(parser, "List: 1; 2; 3", "numbers", [ 1, 2, 3 ])

# -----------------------------------------------------------------------------
# TEST CASE: TestTypeBuilder4Enum
# -----------------------------------------------------------------------------
class TestTypeBuilder4Enum(TestTypeBuilder):

    TYPE_CONVERTERS = [ parse_yesno ]

    def ensure_can_parse_all_enum_values(self, parser, type_converter, schema, name):
        # -- ENSURE: Known enum values are correctly extracted.
        for value_name, value in type_converter.mappings.items():
            text = schema % value_name
            self.assert_match(parser, text, name,  value)

    def test_parse_enum_yesno(self):
        extra_types = self.build_type_dict([ parse_yesno ])
        format_ = "Answer: {answer:YesNo}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.ensure_can_parse_all_enum_values(parser,
                parse_yesno, "Answer: %s", "answer")

        # -- VALID:
        self.assert_match(parser, "Answer: yes", "answer", True)
        self.assert_match(parser, "Answer: no",  "answer", False)

        # -- IGNORE-CASE: In parsing, calls type converter function !!!
        self.assert_match(parser, "Answer: YES", "answer", True)

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "Answer: __YES__", "answer")
        self.assert_mismatch(parser, "Answer: yes ",    "answer")
        self.assert_mismatch(parser, "Answer: yes ZZZ", "answer")

    def test_make_enum(self):
        parse_nword = TypeBuilder.make_enum({"one": 1, "two": 2, "three": 3})
        parse_nword.name = "NumberAsWord"

        extra_types = self.build_type_dict([ parse_nword ])
        format_ = "Answer: {number:NumberAsWord}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.ensure_can_parse_all_enum_values(parser,
            parse_nword, "Answer: %s", "number")

        # -- VALID:
        self.assert_match(parser, "Answer: one", "number", 1)
        self.assert_match(parser, "Answer: two", "number", 2)

        # -- IGNORE-CASE: In parsing, calls type converter function !!!
        self.assert_match(parser, "Answer: THREE", "number", 3)

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "Answer: __one__", "number")
        self.assert_mismatch(parser, "Answer: one ",    "number")
        self.assert_mismatch(parser, "Answer: one_",    "number")
        self.assert_mismatch(parser, "Answer: one ZZZ", "number")

# -----------------------------------------------------------------------------
# TEST CASE: TestTypeBuilder4Choice
# -----------------------------------------------------------------------------
class TestTypeBuilder4Choice(TestTypeBuilder):

    def ensure_can_parse_all_choices(self, parser, type_converter, schema, name):
        for choice_value in type_converter.choices:
            text = schema % choice_value
            self.assert_match(parser, text, name,  choice_value)

    def ensure_can_parse_all_choices2(self, parser, type_converter, schema, name):
        for index, choice_value in enumerate(type_converter.choices):
            text = schema % choice_value
            self.assert_match(parser, text, name, (index, choice_value))

    def test_parse_choice_persons(self):
        extra_types = self.build_type_dict([ parse_person_choice ])
        format_ = "Answer: {answer:PersonChoice}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "Answer: Alice", "answer", "Alice")
        self.assert_match(parser, "Answer: Bob",   "answer", "Bob")
        self.ensure_can_parse_all_choices(parser,
                    parse_person_choice, "Answer: %s", "answer")

        # -- IGNORE-CASE: In parsing, calls type converter function !!!
        # SKIP-WART: self.assert_match(parser, "Answer: BOB", "answer", "BOB")

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "Answer: __Alice__", "answer")
        self.assert_mismatch(parser, "Answer: Alice ",    "answer")
        self.assert_mismatch(parser, "Answer: Alice ZZZ", "answer")

    def test_make_choice(self):
        parse_choice = TypeBuilder.make_choice(["one", "two", "three"])
        parse_choice.name = "NumberWordChoice"
        extra_types = self.build_type_dict([ parse_choice ])
        format_ = "Answer: {answer:NumberWordChoice}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "Answer: one", "answer", "one")
        self.assert_match(parser, "Answer: two", "answer", "two")
        self.ensure_can_parse_all_choices(parser,
                    parse_choice, "Answer: %s", "answer")

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "Answer: __one__", "answer")
        self.assert_mismatch(parser, "Answer: one ",    "answer")
        self.assert_mismatch(parser, "Answer: one ZZZ", "answer")

    def test_make_choice2(self):
        parse_choice2 = TypeBuilder.make_choice2(["zero", "one", "two"])
        parse_choice2.name = "NumberWordChoice2"
        extra_types = self.build_type_dict([ parse_choice2 ])
        format_ = "Answer: {answer:NumberWordChoice2}"
        parser  = parse.Parser(format_, extra_types)

        # -- PERFORM TESTS:
        self.assert_match(parser, "Answer: zero", "answer", (0, "zero"))
        self.assert_match(parser, "Answer: one",  "answer", (1, "one"))
        self.assert_match(parser, "Answer: two",  "answer", (2, "two"))
        self.ensure_can_parse_all_choices2(parser,
                parse_choice2, "Answer: %s", "answer")

        # -- PARSE MISMATCH:
        self.assert_mismatch(parser, "Answer: __one__", "answer")
        self.assert_mismatch(parser, "Answer: one ",    "answer")
        self.assert_mismatch(parser, "Answer: one ZZZ", "answer")

# -----------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()


# Copyright (c) 2012 by jenisys (https://github/jenisys/)
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
