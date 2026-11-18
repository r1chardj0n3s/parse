"""Regression tests for the ``%%`` literal-percent escape in datetime formats."""
from datetime import datetime

import parse


def test_datetime_format_literal_percent():
    # %% is the strptime escape for a literal '%'; it must match a single
    # percent sign, not two
    r = parse.parse("a {:%Y-%%-%H} b", "a 2026-%-10 b")
    assert r[0] == datetime(2026, 1, 1, 10, 0)


def test_datetime_format_literal_percent_roundtrip():
    # datetime.strftime renders %% as one '%'; parse must read it back
    d = datetime(2026, 11, 12, 10, 30)
    text = d.strftime("%Y-%%-%H")
    assert text == "2026-%-10"
    r = parse.parse("a {:%Y-%%-%H} b", "a " + text + " b")
    assert r[0] == datetime(2026, 1, 1, 10, 0)


def test_datetime_format_literal_percent_double_no_match():
    # two consecutive percents in the input no longer satisfy a single %%
    r = parse.parse("a {:%Y-%%} b", "a 2026-%% b")
    assert r is None
