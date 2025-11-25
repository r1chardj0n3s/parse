from typing import assert_type
from parse import Parser, Result, Match, parse, search, findall, ResultIterator

# NB: When checking for ResultIterator[Result], we need to use a string literal,
# because the "real" ResultIterator is not a generic type at runtime.


def test_parse():
    result = parse("{:d} {:d}", "123 456")
    assert_type(result, Result | None)

    result = parse("{:d} {:d}", "123 456", evaluate_result=True)
    assert_type(result, Result | None)

    match = parse("{:d} {:d}", "123 456", evaluate_result=False)
    assert_type(match, Match | None)


def test_search():
    result = search("{:d} {:d}", "123 456")
    assert_type(result, Result | None)

    result = search("{:d} {:d}", "123 456", evaluate_result=True)
    assert_type(result, Result | None)

    match = search("{:d} {:d}", "123 456", evaluate_result=False)
    assert_type(match, Match | None)


def test_findall():
    result_iterator = findall("{:d} {:d}", "123 456 789 012")
    assert_type(result_iterator, "ResultIterator[Result]")

    result_iterator = findall("{:d} {:d}", "123 456 789 012", evaluate_result=True)
    assert_type(result_iterator, "ResultIterator[Result]")

    match_iterator = findall("{:d} {:d}", "123 456 789 012", evaluate_result=False)
    assert_type(match_iterator, "ResultIterator[Match]")


def test_parser():
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
