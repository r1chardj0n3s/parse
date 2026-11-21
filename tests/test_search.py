import parse


def test_basic():
    r = parse.search("a {} c", " a b c ")
    assert r.fixed == ("b",)


def test_multiline():
    r = parse.search("age: {:d}\n", "name: Rufus\nage: 42\ncolor: red\n")
    assert r.fixed == (42,)


def test_pos():
    r = parse.search("a {} c", " a b c ", 2)
    assert r is None


def test_no_evaluate_result():
    match = parse.search(
        "age: {:d}\n", "name: Rufus\nage: 42\ncolor: red\n", evaluate_result=False
    )
    r = match.evaluate_result()
    assert r.fixed == (42,)


def test_d_type_base_prefix():
    # the decimal alternative was tried first and stopped at the "0" of a
    # 0x/0b/0o prefix, so search() returned 0
    assert parse.search("{:d}", "0x1F")[0] == 31
    assert parse.search("{:d}", "0b101")[0] == 5
    assert parse.search("{:d}", "0o17")[0] == 15
    assert parse.search("mask={:d}", "mask=-0x1F;")[0] == -31
    assert parse.search("{:d}", "0xg")[0] == 0
    assert parse.search("{w:d}x{h:d}", "0x10").named == {"w": 0, "h": 10}
