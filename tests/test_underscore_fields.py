import parse


def test_underscore_names():
    for name in ("_", "_value", "__value"):
        result = parse.parse("{" + name + "}", "hello")
        assert result.fixed == ()
        assert result.named == {name: "hello"}
        assert result[name] == "hello"
        assert result.spans == {name: (0, 5)}


def test_underscore_names_with_fixed_fields():
    result = parse.parse("{} {_number:d} {1} {word}", "first 42 second third")
    assert result.fixed == ("first", "second")
    assert result.named == {"_number": 42, "word": "third"}
    assert result.spans == {
        0: (0, 5),
        "_number": (6, 8),
        1: (9, 15),
        "word": (16, 21),
    }


def test_underscore_names_repeated():
    result = parse.parse("{_number:d} {_number:d}", "12 12")
    assert result.fixed == ()
    assert result.named == {"_number": 12}
    assert parse.parse("{_number:d} {_number:d}", "12 13") is None
    assert parse.parse("{_value} {_value}", "hello goodbye") is None


def test_underscore_names_with_dictionary_keys():
    result = parse.parse("{_root[item]} {_root[nested][value]}", "hello world")
    assert result.fixed == ()
    assert result.named == {"_root": {"item": "hello", "nested": {"value": "world"}}}
    assert result.spans == {
        "_root[item]": (0, 5),
        "_root[nested][value]": (6, 11),
    }


def test_underscore_names_with_dots():
    result = parse.parse("{_a.b} {_a_b}", "hello world")
    assert result.fixed == ()
    assert result.named == {"_a.b": "hello", "_a_b": "world"}
    assert result.spans == {"_a.b": (0, 5), "_a_b": (6, 11)}
