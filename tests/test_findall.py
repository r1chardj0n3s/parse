import re
from itertools import islice

import parse


def test_findall():
    s = "".join(
        r.fixed[0] for r in parse.findall(">{}<", "<p>some <b>bold</b> text</p>")
    )
    assert s == "some bold text"


def test_no_evaluate_result():
    s = "".join(
        m.evaluate_result().fixed[0]
        for m in parse.findall(
            ">{}<", "<p>some <b>bold</b> text</p>", evaluate_result=False
        )
    )
    assert s == "some bold text"


def test_case_sensitivity():
    l = [r.fixed[0] for r in parse.findall("x({})x", "X(hi)X")]
    assert l == ["hi"]

    l = [r.fixed[0] for r in parse.findall("x({})x", "X(hi)X", case_sensitive=True)]
    assert l == []


def test_empty_format_terminates():
    results = list(islice(parse.findall("", "ab"), 4))
    assert len(results) == 3
    assert all(result.fixed == () for result in results)


def test_empty_custom_pattern_advances():
    @parse.with_pattern(r".*?")
    def text(value):
        return value

    for evaluate in (True, False):
        matches = parse.findall(
            "{value:Text}",
            "ab",
            extra_types={"Text": text},
            evaluate_result=evaluate,
        )
        results = list(islice(matches, 6))
        if not evaluate:
            results = [match.evaluate_result() for match in results]
        expected = list(re.finditer(r".*?", "ab"))
        assert [result["value"] for result in results] == [m.group() for m in expected]
        assert [result.spans["value"] for result in results] == [m.span() for m in expected]


def test_empty_format_with_search_bounds():
    matches = parse.compile("").findall("abcd", pos=1, endpos=2)
    assert len(list(islice(matches, 3))) == 2
