"""Regression tests for repeated named fields with equivalent formats.

A repeated named field is matched by a back-reference, so the *same text*
must appear at every occurrence.  These tests verify that compiling a
template with a repeated name is only rejected when the two format specs
select different value *types*; decorations that do not change the converter
(width, precision, alignment, sign, grouping) are accepted.
"""
import parse
import pytest


def test_repeated_field_same_type_different_precision():
    p = parse.compile("{n:.2f} or {n:f}")
    r = p.parse("1.23 or 1.23")
    assert r["n"] == 1.23


def test_repeated_field_same_type_different_width():
    p = parse.compile("{n:10} or {n}")
    r = p.parse("1234567890 or 1234567890")
    assert r["n"] == "1234567890"


def test_repeated_field_same_type_different_alignment():
    p = parse.compile("{n:<10} and {n:>4}")
    r = p.parse("Bobxyzabcd and Bobxyzabcd")
    assert r["n"] == "Bobxyzabcd"


def test_repeated_field_sign_decoration():
    p = parse.compile("{n:+d} / {n:d}")
    r = p.parse("42 / 42")
    assert r["n"] == 42


def test_repeated_field_grouping_decoration():
    p = parse.compile("{n:,d} / {n:d}")
    r = p.parse("1000 / 1000")
    assert r["n"] == 1000


def test_repeated_field_mismatched_converters_still_rejected():
    # different value types must still raise
    with pytest.raises(parse.RepeatedNameError):
        parse.compile("{n:d} {n:w}")
    with pytest.raises(parse.RepeatedNameError):
        parse.compile("{n:d} {n}")
    with pytest.raises(parse.RepeatedNameError):
        parse.compile("{n:f} {n:d}")


def test_repeated_field_existing_matching_spec_still_works():
    p = parse.compile("{n:d} and {n:d}")
    r = p.parse("42 and 42")
    assert r["n"] == 42
    with pytest.raises(parse.RepeatedNameError):
        parse.compile("{n:d} and {n:d} and {n:w}")
