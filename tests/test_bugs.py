import pickle
import sys
from copy import deepcopy
from datetime import datetime
from datetime import time

import pytest

import parse


def test_tz_compare_to_None():
    utc = parse.FixedTzOffset(0, "UTC")
    assert utc is not None
    assert utc != "spam"


def test_named_date_issue7():
    r = parse.parse("on {date:ti}", "on 2012-09-17")
    assert r["date"] == datetime(2012, 9, 17, 0, 0, 0)

    # fix introduced regressions
    r = parse.parse("a {:ti} b", "a 1997-07-16T19:20 b")
    assert r[0] == datetime(1997, 7, 16, 19, 20, 0)
    r = parse.parse("a {:ti} b", "a 1997-07-16T19:20Z b")
    utc = parse.FixedTzOffset(0, "UTC")
    assert r[0] == datetime(1997, 7, 16, 19, 20, tzinfo=utc)
    r = parse.parse("a {date:ti} b", "a 1997-07-16T19:20Z b")
    assert r["date"] == datetime(1997, 7, 16, 19, 20, tzinfo=utc)


def test_dotted_type_conversion_pull_8():
    # test pull request 8 which fixes type conversion related to dotted
    # names being applied correctly
    r = parse.parse("{a.b:d}", "1")
    assert r["a.b"] == 1
    r = parse.parse("{a_b:w} {a.b:d}", "1 2")
    assert r["a_b"] == "1"
    assert r["a.b"] == 2


def test_pm_overflow_issue16():
    r = parse.parse("Meet at {:tg}", "Meet at 1/2/2011 12:45 PM")
    assert r[0] == datetime(2011, 2, 1, 12, 45)


def test_pm_handling_issue57():
    r = parse.parse("Meet at {:tg}", "Meet at 1/2/2011 12:15 PM")
    assert r[0] == datetime(2011, 2, 1, 12, 15)
    r = parse.parse("Meet at {:tg}", "Meet at 1/2/2011 12:15 AM")
    assert r[0] == datetime(2011, 2, 1, 0, 15)


def test_user_type_with_group_count_issue60():
    @parse.with_pattern(r"((\w+))", regex_group_count=2)
    def parse_word_and_covert_to_uppercase(text):
        return text.strip().upper()

    @parse.with_pattern(r"\d+")
    def parse_number(text):
        return int(text)

    # -- CASE: Use named (OK)
    type_map = {"Name": parse_word_and_covert_to_uppercase, "Number": parse_number}
    r = parse.parse(
        "Hello {name:Name} {number:Number}", "Hello Alice 42", extra_types=type_map
    )
    assert r.named == {"name": "ALICE", "number": 42}

    # -- CASE: Use unnamed/fixed (problematic)
    r = parse.parse("Hello {:Name} {:Number}", "Hello Alice 42", extra_types=type_map)
    assert r[0] == "ALICE"
    assert r[1] == 42


def test_unmatched_brace_doesnt_match():
    r = parse.parse("{who.txt", "hello")
    assert r is None


def test_pickling_bug_110():
    p = parse.compile("{a:d}")
    # prior to the fix, this would raise an AttributeError
    pickle.dumps(p)


@pytest.mark.parametrize("protocol", [None] + list(range(pickle.HIGHEST_PROTOCOL + 1)))
@pytest.mark.parametrize(
    "format, string",
    [
        ("{:ti}", "2026-11-02T10:30:00Z"),
        ("{:ti}", "2026-11-02T10:30:00.501902+08:00"),
        ("{:ti}", "2026-11-02T10:30:00-05:30"),
        ("{:ti}", "2026-11-02T10:30:00+00:00"),
        ("{:tt}", "10:30 +0800"),
        ("{:tt}", "10:30:00.123456 -0530"),
        ("{:ti}", "2026-11-02T10:30:00"),
        ("{:tt}", "10:30"),
        pytest.param(
            "{:%Y-%m-%dT%H:%M:%S%z}",
            "2026-11-02T10:30:00+08:00",
            marks=pytest.mark.skipif(
                sys.version_info[0] < 3, reason="Python 3+ required for timezone support"
            ),
        ),
    ],
)
def test_copying_datetime_results(format, string, protocol):
    result = parse.parse(format + " {label}", string + " sentinel")
    assert result is not None
    if protocol is None:
        restored = deepcopy(result)
    else:
        restored = pickle.loads(pickle.dumps(result, protocol))
    assert restored is not result
    assert restored.fixed == result.fixed
    assert restored.named == result.named
    assert restored.spans == result.spans
    assert type(restored[0]) is type(result[0])
    assert type(restored[0].tzinfo) is type(result[0].tzinfo)
    assert restored[0].utcoffset() == result[0].utcoffset()
    assert restored[0].tzname() == result[0].tzname()


def test_unused_centered_alignment_bug():
    r = parse.parse("{:^2S}", "foo")
    assert r[0] == "foo"
    r = parse.search("{:^2S}", "foo")
    assert r[0] == "foo"

    # specifically test for the case in issue #118 as well
    r = parse.parse("Column {:d}:{:^}", "Column 1: Timestep")
    assert r[0] == 1
    assert r[1] == "Timestep"


def test_unused_left_alignment_bug():
    r = parse.parse("{:<2S}", "foo")
    assert r[0] == "foo"
    r = parse.search("{:<2S}", "foo")
    assert r[0] == "foo"


def test_match_trailing_newline():
    r = parse.parse("{}", "test\n")
    assert r[0] == "test\n"


def test_case_insensitive_month_names():
    # matching is case-insensitive by default, so a month name may arrive in
    # any case and the conversion must not be case-sensitive
    cases = [
        ("{:tg}", "1/jul/2011", datetime(2011, 7, 1)),
        ("{:tg}", "1/jULy/2011 13:05", datetime(2011, 7, 1, 13, 5)),
        ("{:ta}", "JUL/16/2011", datetime(2011, 7, 16)),
        ("{:te}", "Mon, 16 jul 1997 19:20 +0200", datetime(1997, 7, 16, 19, 20)),
        ("{:th}", "16/JUL/1997:19:20 +0000", datetime(1997, 7, 16, 19, 20)),
        ("{:tc}", "mon jul 16 19:20 1997", datetime(1997, 7, 16, 19, 20)),
    ]
    for format, string, expected in cases:
        result = parse.parse(format, string)
        assert result is not None, (format, string)
        assert result[0].replace(tzinfo=None) == expected, (format, string)

    # the ts type carries no year, so just check the month/day it resolved
    result = parse.parse("{:ts}", "jul 16 19:20:20")
    assert result is not None
    assert (result[0].month, result[0].day) == (7, 16)


def test_microsecond_precision_issue162():
    # fractional seconds that previously suffered floating-point rounding
    r = parse.parse("{:ti}", "2023-10-14T15:09:08.501902Z")
    assert r[0].microsecond == 501902

    # fewer than 6 fractional digits should be zero-padded
    r = parse.parse("{:ti}", "2023-10-14T15:09:08.1Z")
    assert r[0].microsecond == 100000

    # exactly 6 fractional digits
    r = parse.parse("{:ti}", "2023-10-14T15:09:08.123456Z")
    assert r[0].microsecond == 123456

    # more than 6 fractional digits should be truncated
    r = parse.parse("{:ti}", "2023-10-14T15:09:08.1234567Z")
    assert r[0].microsecond == 123456


def test_time_type_requires_an_actual_time():
    # the "tt" pattern marked the time itself as optional, so a field could
    # match nothing at all and convert that into a bogus time(0, 0)
    assert parse.parse("{:tt}", "") is None
    assert parse.parse("Meet at {:tt}", "Meet at ") is None
    assert parse.search("{:tt}", "there is no time here") is None

    # the phantom empty match also showed up as an endless stream of results
    phantom = [result for _, result in zip(range(5), parse.findall("{:tt}", "no time"))]
    assert phantom == []

    # the documented time forms still parse
    assert parse.parse("{:tt}", "10:21:36 PM")[0] == time(22, 21, 36)
    assert parse.parse("Meet at {:tt}", "Meet at 10:21")[0] == time(10, 21)


def test_leading_space_with_base_prefix():
    # the "d" type regex accepts a single leading space (the " " sign
    # option), but int_convert() only looked for a 0b/0o/0x prefix right
    # after an optional + or - sign, so a space-prefixed number lost its
    # base and was silently misread as decimal, e.g. " 0x1f" -> 1
    assert parse.parse("{:d}", " 0x1f")[0] == 0x1F
    assert parse.parse("{:d}", " 0b101")[0] == 0b101
    assert parse.parse("{:d}", " 0o17")[0] == 0o17
    assert parse.parse("{: d}", " 0x1f")[0] == 0x1F

    # same two-space shape as the passing "a {:d} b" / "a  12 b" case
    assert parse.parse("a {:d} b", "a  0x1000 b")[0] == 4096

    # decimal values with a leading space are unchanged
    assert parse.parse("{:d}", " 12")[0] == 12
    assert parse.parse("{:d}", "-12")[0] == -12
    assert parse.parse("{:d}", "+12")[0] == 12
