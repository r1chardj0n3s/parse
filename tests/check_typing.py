# This file contains tests that check the type annotations in parse/__init__.pyi.
# It is not to be run with pytest, but is instead meant to be checked with mypy.

# Use typing_extensions because we want to be compatible with Python 3.10
from typing_extensions import assert_type

from parse import findall
from parse import Match
from parse import parse
from parse import Parser
from parse import Result
from parse import ResultIterator
from parse import search

# NB: When checking for ResultIterator[Result], we need to use a string literal,
# because the "real" ResultIterator is not a generic type at runtime.


def test_parse() -> None:
    result = parse("{:d} {:d}", "123 456")
    assert_type(result, Result | None)

    result = parse("{:d} {:d}", "123 456", evaluate_result=True)
    assert_type(result, Result | None)

    match = parse("{:d} {:d}", "123 456", evaluate_result=False)
    assert_type(match, Match | None)


def test_search() -> None:
    result = search("{:d} {:d}", "123 456")
    assert_type(result, Result | None)

    result = search("{:d} {:d}", "123 456", evaluate_result=True)
    assert_type(result, Result | None)

    match = search("{:d} {:d}", "123 456", evaluate_result=False)
    assert_type(match, Match | None)


def test_findall() -> None:
    result_iterator = findall("{:d} {:d}", "123 456 789 012")
    assert_type(result_iterator, "ResultIterator[Result]")

    result_iterator = findall("{:d} {:d}", "123 456 789 012", evaluate_result=True)
    assert_type(result_iterator, "ResultIterator[Result]")

    match_iterator = findall("{:d} {:d}", "123 456 789 012", evaluate_result=False)
    assert_type(match_iterator, "ResultIterator[Match]")


def test_parser() -> None:
    parser = Parser("{a:d} {:d}")

    result = parser.parse("123 456")
    assert_type(result, Result | None)

    result = parser.parse("123 456", evaluate_result=True)
    assert_type(result, Result | None)

    match = parser.parse("123 456", evaluate_result=False)
    assert_type(match, Match | None)

    result = parser.search("123 456")
    assert_type(result, Result | None)

    result = parser.search("123 456", evaluate_result=True)
    assert_type(result, Result | None)

    match = parser.search("123 456", evaluate_result=False)
    assert_type(match, Match | None)

    result_iterator = parser.findall("123 456 789 012")
    assert_type(result_iterator, "ResultIterator[Result]")

    result_iterator = parser.findall("123 456 789 012", evaluate_result=True)
    assert_type(result_iterator, "ResultIterator[Result]")

    match_iterator = parser.findall("123 456 789 012", evaluate_result=False)
    assert_type(match_iterator, "ResultIterator[Match]")

    assert_type(parser.format, str)
    assert_type(parser.fixed_fields, list[int])
    assert_type(parser.named_fields, list[str])
