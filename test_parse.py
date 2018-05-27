# -*- encoding: utf8 -*-
'''Test suite for parse.py

This code is copyright 2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
'''

import unittest
from datetime import datetime, time
from decimal import Decimal
import re

import parse


class TestPattern(unittest.TestCase):
    def _test_expression(self, format, expression):
        self.assertEqual(parse.Parser(format)._expression, expression)

    def test_braces(self):
        # pull a simple string out of another string
        self._test_expression('{{ }}', '\{ \}')

    def test_fixed(self):
        # pull a simple string out of another string
        self._test_expression('{}', '(.+?)')
        self._test_expression('{} {}', '(.+?) (.+?)')

    def test_named(self):
        # pull a named string out of another string
        self._test_expression('{name}', '(?P<name>.+?)')
        self._test_expression('{name} {other}',
            '(?P<name>.+?) (?P<other>.+?)')

    def test_named_typed(self):
        # pull a named string out of another string
        self._test_expression('{name:w}', '(?P<name>\w+)')
        self._test_expression('{name:w} {other:w}',
            '(?P<name>\w+) (?P<other>\w+)')

    def test_beaker(self):
        # skip some trailing whitespace
        self._test_expression('{:<}', '(.+?) *')

    def test_left_fill(self):
        # skip some trailing periods
        self._test_expression('{:.<}', '(.+?)\.*')

    def test_bird(self):
        # skip some trailing whitespace
        self._test_expression('{:>}', ' *(.+?)')

    def test_center(self):
        # skip some surrounding whitespace
        self._test_expression('{:^}', ' *(.+?) *')

    def test_format_variety(self):
        def _(fmt, matches):
            d = parse.extract_format(fmt, {'spam': 'spam'})
            for k in matches:
                self.assertEqual(d.get(k), matches[k],
                    'm["%s"]=%r, expect %r' % (k, d.get(k), matches[k]))

        for t in '%obxegfdDwWsS':
            _(t, dict(type=t))
            _('10' + t, dict(type=t, width='10'))
        _('05d', dict(type='d', width='5', zero=True))
        _('<', dict(align='<'))
        _('.<', dict(align='<', fill='.'))
        _('>', dict(align='>'))
        _('.>', dict(align='>', fill='.'))
        _('^', dict(align='^'))
        _('.^', dict(align='^', fill='.'))
        _('x=d', dict(type='d', align='=', fill='x'))
        _('d', dict(type='d'))
        _('ti', dict(type='ti'))
        _('spam', dict(type='spam'))

        _('.^010d', dict(type='d', width='10', align='^', fill='.',
            zero=True))
        _('.2f', dict(type='f', precision='2'))
        _('10.2f', dict(type='f', width='10', precision='2'))

    def test_dot_separated_fields(self):
        # this should just work and provide the named value
        res = parse.parse('{hello.world}_{jojo.foo.baz}_{simple}', 'a_b_c')
        assert res.named['hello.world'] == 'a'
        assert res.named['jojo.foo.baz'] == 'b'
        assert res.named['simple'] == 'c'

    def test_dict_style_fields(self):
        res = parse.parse('{hello[world]}_{hello[foo][baz]}_{simple}', 'a_b_c')
        assert res.named['hello']['world'] == 'a'
        assert res.named['hello']['foo']['baz'] == 'b'
        assert res.named['simple'] == 'c'

    def test_dot_separated_fields_name_collisions(self):
        # this should just work and provide the named value
        res = parse.parse('{a_.b}_{a__b}_{a._b}_{a___b}', 'a_b_c_d')
        assert res.named['a_.b'] == 'a'
        assert res.named['a__b'] == 'b'
        assert res.named['a._b'] == 'c'
        assert res.named['a___b'] == 'd'

    def test_invalid_groupnames_are_handled_gracefully(self):
        self.assertRaises(NotImplementedError, parse.parse,
            "{hello['world']}", "doesn't work")


class TestResult(unittest.TestCase):
    def test_fixed_access(self):
        r = parse.Result((1, 2), {}, None)
        self.assertEqual(r[0], 1)
        self.assertEqual(r[1], 2)
        self.assertRaises(IndexError, r.__getitem__, 2)
        self.assertRaises(KeyError, r.__getitem__, 'spam')

    def test_named_access(self):
        r = parse.Result((), {'spam': 'ham'}, None)
        self.assertEqual(r['spam'], 'ham')
        self.assertRaises(KeyError, r.__getitem__, 'ham')
        self.assertRaises(IndexError, r.__getitem__, 0)


class TestParse(unittest.TestCase):
    def test_no_match(self):
        # string does not match format
        self.assertEqual(parse.parse('{{hello}}', 'hello'), None)

    def test_nothing(self):
        # do no actual parsing
        r = parse.parse('{{hello}}', '{hello}')
        self.assertEqual(r.fixed, ())
        self.assertEqual(r.named, {})

    def test_no_evaluate_result(self):
        # pull a fixed value out of string
        match = parse.parse('hello {}', 'hello world', evaluate_result=False)
        r = match.evaluate_result()
        self.assertEqual(r.fixed, ('world', ))

    def test_regular_expression(self):
        # match an actual regular expression
        s = r'^(hello\s[wW]{}!+.*)$'
        e = s.replace('{}', 'orld')
        r = parse.parse(s, e)
        self.assertEqual(r.fixed, ('orld',))
        e = s.replace('{}', '.*?')
        r = parse.parse(s, e)
        self.assertEqual(r.fixed, ('.*?',))

    def test_question_mark(self):
        # issue9: make sure a ? in the parse string is handled correctly
        r = parse.parse('"{}"?', '"teststr"?')
        self.assertEqual(r[0], 'teststr')

    def test_pipe(self):
        # issue22: make sure a | in the parse string is handled correctly
        r = parse.parse('| {}', '| teststr')
        self.assertEqual(r[0], 'teststr')

    def test_unicode(self):
        # issue29: make sure unicode is parsable
        r = parse.parse('{}', u't€ststr')
        self.assertEqual(r[0], u't€ststr')

    def test_hexadecimal(self):
        # issue42: make sure bare hexadecimal isn't matched as "digits"
        r = parse.parse('{:d}', 'abcdef')
        self.assertIsNone(r)

    def test_fixed(self):
        # pull a fixed value out of string
        r = parse.parse('hello {}', 'hello world')
        self.assertEqual(r.fixed, ('world', ))

    def test_left(self):
        # pull left-aligned text out of string
        r = parse.parse('{:<} world', 'hello       world')
        self.assertEqual(r.fixed, ('hello', ))

    def test_right(self):
        # pull right-aligned text out of string
        r = parse.parse('hello {:>}', 'hello       world')
        self.assertEqual(r.fixed, ('world', ))

    def test_center(self):
        # pull center-aligned text out of string
        r = parse.parse('hello {:^} world', 'hello  there     world')
        self.assertEqual(r.fixed, ('there', ))

    def test_typed(self):
        # pull a named, typed values out of string
        r = parse.parse('hello {:d} {:w}', 'hello 12 people')
        self.assertEqual(r.fixed, (12, 'people'))
        r = parse.parse('hello {:w} {:w}', 'hello 12 people')
        self.assertEqual(r.fixed, ('12', 'people'))

    def test_precision(self):
        # pull a float out of a string
        r = parse.parse('Pi = {:.7f}', 'Pi = 3.1415926')
        self.assertEqual(r.fixed, (3.1415926, ))
        r = parse.parse('Pi/10 = {:8.5f}', 'Pi/10 =  0.31415')
        self.assertEqual(r.fixed, (0.31415, ))

    def test_precision_fail(self):
        # floats must have a leading zero
        # IS THIS CORRECT?
        r = parse.parse('Pi/10 = {:8.5f}', 'Pi/10 = .31415')
        self.assertEqual(r, None)

    def test_custom_type(self):
        # use a custom type
        r = parse.parse('{:shouty} {:spam}', 'hello world',
            dict(shouty=lambda s: s.upper(),
                spam=lambda s: ''.join(reversed(s))))
        self.assertEqual(r.fixed, ('HELLO', 'dlrow'))
        r = parse.parse('{:d}', '12', dict(d=lambda s: int(s) * 2))
        self.assertEqual(r.fixed, (24,))
        r = parse.parse('{:d}', '12')
        self.assertEqual(r.fixed, (12,))

    def test_typed_fail(self):
        # pull a named, typed values out of string
        self.assertEqual(parse.parse('hello {:d} {:w}', 'hello people 12'),
            None)

    def test_named(self):
        # pull a named value out of string
        r = parse.parse('hello {name}', 'hello world')
        self.assertEqual(r.named, {'name': 'world'})

    def test_named_repeated(self):
        # test a name may be repeated
        r = parse.parse('{n} {n}', 'x x')
        self.assertEqual(r.named, {'n': 'x'})

    def test_named_repeated_type(self):
        # test a name may be repeated with type conversion
        r = parse.parse('{n:d} {n:d}', '1 1')
        self.assertEqual(r.named, {'n': 1})

    def test_named_repeated_fail_value(self):
        # test repeated name fails if value mismatches
        r = parse.parse('{n} {n}', 'x y')
        self.assertEqual(r, None)

    def test_named_repeated_type_fail_value(self):
        # test repeated name with type conversion fails if value mismatches
        r = parse.parse('{n:d} {n:d}', '1 2')
        self.assertEqual(r, None)

    def test_named_repeated_type_mismatch(self):
        # test repeated name with mismatched type
        self.assertRaises(parse.RepeatedNameError, parse.compile,
            '{n:d} {n:w}')

    def test_mixed(self):
        # pull a fixed and named values out of string
        r = parse.parse('hello {} {name} {} {spam}',
            'hello world and other beings')
        self.assertEqual(r.fixed, ('world', 'other'))
        self.assertEqual(r.named, dict(name='and', spam='beings'))

    def test_named_typed(self):
        # pull a named, typed values out of string
        r = parse.parse('hello {number:d} {things}', 'hello 12 people')
        self.assertEqual(r.named, dict(number=12, things='people'))
        r = parse.parse('hello {number:w} {things}', 'hello 12 people')
        self.assertEqual(r.named, dict(number='12', things='people'))

    def test_named_aligned_typed(self):
        # pull a named, typed values out of string
        r = parse.parse('hello {number:<d} {things}', 'hello 12      people')
        self.assertEqual(r.named, dict(number=12, things='people'))
        r = parse.parse('hello {number:>d} {things}', 'hello      12 people')
        self.assertEqual(r.named, dict(number=12, things='people'))
        r = parse.parse('hello {number:^d} {things}',
            'hello      12      people')
        self.assertEqual(r.named, dict(number=12, things='people'))

    def test_multiline(self):
        r = parse.parse('hello\n{}\nworld', 'hello\nthere\nworld')
        self.assertEqual(r.fixed[0], 'there')

    def test_spans(self):
        # test the string sections our fields come from
        string = 'hello world'
        r = parse.parse('hello {}', string)
        self.assertEqual(r.spans, {0: (6, 11)})
        start, end = r.spans[0]
        self.assertEqual(string[start:end], r.fixed[0])

        string = 'hello     world'
        r = parse.parse('hello {:>}', string)
        self.assertEqual(r.spans, {0: (10, 15)})
        start, end = r.spans[0]
        self.assertEqual(string[start:end], r.fixed[0])

        string = 'hello 0x12 world'
        r = parse.parse('hello {val:x} world', string)
        self.assertEqual(r.spans, {'val': (6, 10)})
        start, end = r.spans['val']
        self.assertEqual(string[start:end], '0x%x' % r.named['val'])

        string = 'hello world and other beings'
        r = parse.parse('hello {} {name} {} {spam}', string)
        self.assertEqual(r.spans, {0: (6, 11), 'name': (12, 15),
            1: (16, 21), 'spam': (22, 28)})

    def test_numbers(self):
        # pull a numbers out of a string
        def y(fmt, s, e, str_equals=False):
            p = parse.compile(fmt)
            r = p.parse(s)
            if r is None:
                self.fail('%r (%r) did not match %r' % (fmt, p._expression, s))
            r = r.fixed[0]
            if str_equals:
                self.assertEqual(str(r), str(e),
                    '%r found %r in %r, not %r' % (fmt, r, s, e))
            else:
                self.assertEqual(r, e,
                    '%r found %r in %r, not %r' % (fmt, r, s, e))

        def n(fmt, s, e):
            if parse.parse(fmt, s) is not None:
                self.fail('%r matched %r' % (fmt, s))
        y('a {:d} b', 'a 0 b', 0)
        y('a {:d} b', 'a 12 b', 12)
        y('a {:5d} b', 'a    12 b', 12)
        y('a {:5d} b', 'a   -12 b', -12)
        y('a {:d} b', 'a -12 b', -12)
        y('a {:d} b', 'a +12 b', 12)
        y('a {:d} b', 'a  12 b', 12)
        y('a {:d} b', 'a 0b1000 b', 8)
        y('a {:d} b', 'a 0o1000 b', 512)
        y('a {:d} b', 'a 0x1000 b', 4096)
        y('a {:d} b', 'a 0xabcdef b', 0xabcdef)

        y('a {:%} b', 'a 100% b', 1)
        y('a {:%} b', 'a 50% b', .5)
        y('a {:%} b', 'a 50.1% b', .501)

        y('a {:n} b', 'a 100 b', 100)
        y('a {:n} b', 'a 1,000 b', 1000)
        y('a {:n} b', 'a 1.000 b', 1000)
        y('a {:n} b', 'a -1,000 b', -1000)
        y('a {:n} b', 'a 10,000 b', 10000)
        y('a {:n} b', 'a 100,000 b', 100000)
        n('a {:n} b', 'a 100,00 b', None)
        y('a {:n} b', 'a 100.000 b', 100000)
        y('a {:n} b', 'a 1.000.000 b', 1000000)

        y('a {:f} b', 'a 12.0 b', 12.0)
        y('a {:f} b', 'a -12.1 b', -12.1)
        y('a {:f} b', 'a +12.1 b', 12.1)
        n('a {:f} b', 'a 12 b', None)

        y('a {:e} b', 'a 1.0e10 b', 1.0e10)
        y('a {:e} b', 'a 1.0E10 b', 1.0e10)
        y('a {:e} b', 'a 1.10000e10 b', 1.1e10)
        y('a {:e} b', 'a 1.0e-10 b', 1.0e-10)
        y('a {:e} b', 'a 1.0e+10 b', 1.0e10)
        # can't actually test this one on values 'cos nan != nan
        y('a {:e} b', 'a nan b', float('nan'), str_equals=True)
        y('a {:e} b', 'a NAN b', float('nan'), str_equals=True)
        y('a {:e} b', 'a inf b', float('inf'))
        y('a {:e} b', 'a +inf b', float('inf'))
        y('a {:e} b', 'a -inf b', float('-inf'))
        y('a {:e} b', 'a INF b', float('inf'))
        y('a {:e} b', 'a +INF b', float('inf'))
        y('a {:e} b', 'a -INF b', float('-inf'))

        y('a {:g} b', 'a 1 b', 1)
        y('a {:g} b', 'a 1e10 b', 1e10)
        y('a {:g} b', 'a 1.0e10 b', 1.0e10)
        y('a {:g} b', 'a 1.0E10 b', 1.0e10)

        y('a {:b} b', 'a 1000 b', 8)
        y('a {:b} b', 'a 0b1000 b', 8)
        y('a {:o} b', 'a 12345670 b', int('12345670', 8))
        y('a {:o} b', 'a 0o12345670 b', int('12345670', 8))
        y('a {:x} b', 'a 1234567890abcdef b', 0x1234567890abcdef)
        y('a {:x} b', 'a 1234567890ABCDEF b', 0x1234567890ABCDEF)
        y('a {:x} b', 'a 0x1234567890abcdef b', 0x1234567890abcdef)
        y('a {:x} b', 'a 0x1234567890ABCDEF b', 0x1234567890ABCDEF)

        y('a {:05d} b', 'a 00001 b', 1)
        y('a {:05d} b', 'a -00001 b', -1)
        y('a {:05d} b', 'a +00001 b', 1)

        y('a {:=d} b', 'a 000012 b', 12)
        y('a {:x=5d} b', 'a xxx12 b', 12)
        y('a {:x=5d} b', 'a -xxx12 b', -12)

    def test_hex_looks_like_binary_issue65(self):
        r = parse.parse('a {:x} b', 'a 0B b')
        self.assertEqual(r[0], 11)
        r = parse.parse('a {:x} b', 'a 0B1 b')
        self.assertEqual(r[0], 1)

    def test_two_datetimes(self):
        r = parse.parse('a {:ti} {:ti} b', 'a 1997-07-16 2012-08-01 b')
        self.assertEqual(len(r.fixed), 2)
        self.assertEqual(r[0], datetime(1997, 7, 16))
        self.assertEqual(r[1], datetime(2012, 8, 1))

    def test_datetimes(self):
        def y(fmt, s, e, tz=None):
            p = parse.compile(fmt)
            r = p.parse(s)
            if r is None:
                self.fail('%r (%r) did not match %r' % (fmt, p._expression, s))
            r = r.fixed[0]
            try:
                self.assertEqual(r, e,
                    '%r found %r in %r, not %r' % (fmt, r, s, e))
            except ValueError:
                self.fail('%r found %r in %r, not %r' % (fmt, r, s, e))

            if tz is not None:
                self.assertEqual(r.tzinfo, tz,
                    '%r found TZ %r in %r, not %r' % (fmt, r.tzinfo, s, e))

        def n(fmt, s, e):
            if parse.parse(fmt, s) is not None:
                self.fail('%r matched %r' % (fmt, s))

        utc = parse.FixedTzOffset(0, 'UTC')
        aest = parse.FixedTzOffset(10 * 60, '+1000')
        tz60 = parse.FixedTzOffset(60, '+01:00')

        # ISO 8660 variants
        # YYYY-MM-DD (eg 1997-07-16)
        y('a {:ti} b', 'a 1997-07-16 b', datetime(1997, 7, 16))

        # YYYY-MM-DDThh:mmTZD (eg 1997-07-16T19:20+01:00)
        y('a {:ti} b', 'a 1997-07-16 19:20 b',
            datetime(1997, 7, 16, 19, 20, 0))
        y('a {:ti} b', 'a 1997-07-16T19:20 b',
            datetime(1997, 7, 16, 19, 20, 0))
        y('a {:ti} b', 'a 1997-07-16T19:20Z b',
            datetime(1997, 7, 16, 19, 20, tzinfo=utc))
        y('a {:ti} b', 'a 1997-07-16T19:20+0100 b',
            datetime(1997, 7, 16, 19, 20, tzinfo=tz60))
        y('a {:ti} b', 'a 1997-07-16T19:20+01:00 b',
            datetime(1997, 7, 16, 19, 20, tzinfo=tz60))
        y('a {:ti} b', 'a 1997-07-16T19:20 +01:00 b',
            datetime(1997, 7, 16, 19, 20, tzinfo=tz60))

        # YYYY-MM-DDThh:mm:ssTZD (eg 1997-07-16T19:20:30+01:00)
        y('a {:ti} b', 'a 1997-07-16 19:20:30 b',
            datetime(1997, 7, 16, 19, 20, 30))
        y('a {:ti} b', 'a 1997-07-16T19:20:30 b',
            datetime(1997, 7, 16, 19, 20, 30))
        y('a {:ti} b', 'a 1997-07-16T19:20:30Z b',
            datetime(1997, 7, 16, 19, 20, 30, tzinfo=utc))
        y('a {:ti} b', 'a 1997-07-16T19:20:30+01:00 b',
            datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz60))
        y('a {:ti} b', 'a 1997-07-16T19:20:30 +01:00 b',
            datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz60))

        # YYYY-MM-DDThh:mm:ss.sTZD (eg 1997-07-16T19:20:30.45+01:00)
        y('a {:ti} b', 'a 1997-07-16 19:20:30.500000 b',
            datetime(1997, 7, 16, 19, 20, 30, 500000))
        y('a {:ti} b', 'a 1997-07-16T19:20:30.500000 b',
            datetime(1997, 7, 16, 19, 20, 30, 500000))
        y('a {:ti} b', 'a 1997-07-16T19:20:30.5Z b',
            datetime(1997, 7, 16, 19, 20, 30, 500000, tzinfo=utc))
        y('a {:ti} b', 'a 1997-07-16T19:20:30.5+01:00 b',
            datetime(1997, 7, 16, 19, 20, 30, 500000, tzinfo=tz60))

        aest_d = datetime(2011, 11, 21, 10, 21, 36, tzinfo=aest)
        dt = datetime(2011, 11, 21, 10, 21, 36)
        dt00 = datetime(2011, 11, 21, 10, 21)
        d = datetime(2011, 11, 21)

        # te   RFC2822 e-mail format        datetime
        y('a {:te} b', 'a Mon, 21 Nov 2011 10:21:36 +1000 b', aest_d)
        y('a {:te} b', 'a Mon, 21 Nov 2011 10:21:36 +10:00 b', aest_d)
        y('a {:te} b', 'a 21 Nov 2011 10:21:36 +1000 b', aest_d)

        # tg   global (day/month) format datetime
        y('a {:tg} b', 'a 21/11/2011 10:21:36 AM +1000 b', aest_d)
        y('a {:tg} b', 'a 21/11/2011 10:21:36 AM +10:00 b', aest_d)
        y('a {:tg} b', 'a 21-11-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:tg} b', 'a 21/11/2011 10:21:36 +1000 b', aest_d)
        y('a {:tg} b', 'a 21/11/2011 10:21:36 b', dt)
        y('a {:tg} b', 'a 21/11/2011 10:21 b', dt00)
        y('a {:tg} b', 'a 21-11-2011 b', d)
        y('a {:tg} b', 'a 21-Nov-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:tg} b', 'a 21-November-2011 10:21:36 AM +1000 b', aest_d)

        # ta   US (month/day) format     datetime
        y('a {:ta} b', 'a 11/21/2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a 11/21/2011 10:21:36 AM +10:00 b', aest_d)
        y('a {:ta} b', 'a 11-21-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a 11/21/2011 10:21:36 +1000 b', aest_d)
        y('a {:ta} b', 'a 11/21/2011 10:21:36 b', dt)
        y('a {:ta} b', 'a 11/21/2011 10:21 b', dt00)
        y('a {:ta} b', 'a 11-21-2011 b', d)
        y('a {:ta} b', 'a Nov-21-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a November-21-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a November-21-2011 b', d)

        # ts   Linux System log format        datetime
        y('a {:ts} b', 'a Nov 21 10:21:36 b',  datetime(datetime.today().year, 11, 21, 10, 21, 36))
        y('a {:ts} b', 'a Nov  1 10:21:36 b',  datetime(datetime.today().year, 11, 1, 10, 21, 36))
        y('a {:ts} b', 'a Nov  1 03:21:36 b',  datetime(datetime.today().year, 11, 1, 3, 21, 36))

        # th   HTTP log format date/time                   datetime
        y('a {:th} b', 'a 21/Nov/2011:10:21:36 +1000 b', aest_d)
        y('a {:th} b', 'a 21/Nov/2011:10:21:36 +10:00 b', aest_d)

        d = datetime(2011, 11, 21, 10, 21, 36)

        # tc   ctime() format           datetime
        y('a {:tc} b', 'a Mon Nov 21 10:21:36 2011 b', d)

        t530 = parse.FixedTzOffset(-5 * 60 - 30, '-5:30')
        t830 = parse.FixedTzOffset(-8 * 60 - 30, '-8:30')

        # tt   Time                                        time
        y('a {:tt} b', 'a 10:21:36 AM +1000 b', time(10, 21, 36, tzinfo=aest))
        y('a {:tt} b', 'a 10:21:36 AM +10:00 b', time(10, 21, 36, tzinfo=aest))
        y('a {:tt} b', 'a 10:21:36 AM b', time(10, 21, 36))
        y('a {:tt} b', 'a 10:21:36 PM b', time(22, 21, 36))
        y('a {:tt} b', 'a 10:21:36 b', time(10, 21, 36))
        y('a {:tt} b', 'a 10:21 b', time(10, 21))
        y('a {:tt} b', 'a 10:21:36 PM -5:30 b', time(22, 21, 36, tzinfo=t530))
        y('a {:tt} b', 'a 10:21:36 PM -530 b', time(22, 21, 36, tzinfo=t530))
        y('a {:tt} b', 'a 10:21:36 PM -05:30 b', time(22, 21, 36, tzinfo=t530))
        y('a {:tt} b', 'a 10:21:36 PM -0530 b', time(22, 21, 36, tzinfo=t530))
        y('a {:tt} b', 'a 10:21:36 PM -08:30 b', time(22, 21, 36, tzinfo=t830))
        y('a {:tt} b', 'a 10:21:36 PM -0830 b', time(22, 21, 36, tzinfo=t830))

    def test_datetime_group_count(self):
        # test we increment the group count correctly for datetimes
        r = parse.parse('{:ti} {}', '1972-01-01 spam')
        self.assertEqual(r.fixed[1], 'spam')
        r = parse.parse('{:tg} {}', '1-1-1972 spam')
        self.assertEqual(r.fixed[1], 'spam')
        r = parse.parse('{:ta} {}', '1-1-1972 spam')
        self.assertEqual(r.fixed[1], 'spam')
        r = parse.parse('{:th} {}', '21/Nov/2011:10:21:36 +1000 spam')
        self.assertEqual(r.fixed[1], 'spam')
        r = parse.parse('{:te} {}', '21 Nov 2011 10:21:36 +1000 spam')
        self.assertEqual(r.fixed[1], 'spam')
        r = parse.parse('{:tc} {}', 'Mon Nov 21 10:21:36 2011 spam')
        self.assertEqual(r.fixed[1], 'spam')
        r = parse.parse('{:tt} {}', '10:21 spam')
        self.assertEqual(r.fixed[1], 'spam')

    def test_mixed_types(self):
        # stress-test: pull one of everything out of a string
        r = parse.parse('''
            letters: {:w}
            non-letters: {:W}
            whitespace: "{:s}"
            non-whitespace: \t{:S}\n
            digits: {:d} {:d}
            non-digits: {:D}
            numbers with thousands: {:n}
            fixed-point: {:f}
            floating-point: {:e}
            general numbers: {:g} {:g}
            binary: {:b}
            octal: {:o}
            hex: {:x}
            ISO 8601 e.g. {:ti}
            RFC2822 e.g. {:te}
            Global e.g. {:tg}
            US e.g. {:ta}
            ctime() e.g. {:tc}
            HTTP e.g. {:th}
            time: {:tt}
            final value: {}
        ''',
        '''
            letters: abcdef_GHIJLK
            non-letters: !@#%$ *^%
            whitespace: "   \t\n"
            non-whitespace: \tabc\n
            digits: 12345 0b1011011
            non-digits: abcdef
            numbers with thousands: 1,000
            fixed-point: 100.2345
            floating-point: 1.1e-10
            general numbers: 1 1.1
            binary: 0b1000
            octal: 0o1000
            hex: 0x1000
            ISO 8601 e.g. 1972-01-20T10:21:36Z
            RFC2822 e.g. Mon, 20 Jan 1972 10:21:36 +1000
            Global e.g. 20/1/1972 10:21:36 AM +1:00
            US e.g. 1/20/1972 10:21:36 PM +10:30
            ctime() e.g. Sun Sep 16 01:03:52 1973
            HTTP e.g. 21/Nov/2011:00:07:11 +0000
            time: 10:21:36 PM -5:30
            final value: spam
        ''')
        self.assertNotEqual(r, None)
        self.assertEqual(r.fixed[22], 'spam')

    def test_mixed_type_variant(self):
        r = parse.parse('''
            letters: {:w}
            non-letters: {:W}
            whitespace: "{:s}"
            non-whitespace: \t{:S}\n
            digits: {:d}
            non-digits: {:D}
            numbers with thousands: {:n}
            fixed-point: {:f}
            floating-point: {:e}
            general numbers: {:g} {:g}
            binary: {:b}
            octal: {:o}
            hex: {:x}
            ISO 8601 e.g. {:ti}
            RFC2822 e.g. {:te}
            Global e.g. {:tg}
            US e.g. {:ta}
            ctime() e.g. {:tc}
            HTTP e.g. {:th}
            time: {:tt}
            final value: {}
        ''',
        '''
            letters: abcdef_GHIJLK
            non-letters: !@#%$ *^%
            whitespace: "   \t\n"
            non-whitespace: \tabc\n
            digits: 0xabcdef
            non-digits: abcdef
            numbers with thousands: 1.000.000
            fixed-point: 0.00001
            floating-point: NAN
            general numbers: 1.1e10 nan
            binary: 0B1000
            octal: 0O1000
            hex: 0X1000
            ISO 8601 e.g. 1972-01-20T10:21:36Z
            RFC2822 e.g. Mon, 20 Jan 1972 10:21:36 +1000
            Global e.g. 20/1/1972 10:21:36 AM +1:00
            US e.g. 1/20/1972 10:21:36 PM +10:30
            ctime() e.g. Sun Sep 16 01:03:52 1973
            HTTP e.g. 21/Nov/2011:00:07:11 +0000
            time: 10:21:36 PM -5:30
            final value: spam
        ''')
        self.assertNotEqual(r, None)
        self.assertEqual(r.fixed[21], 'spam')

    def test_too_many_fields(self):
        # Python 3.5 removed the limit of 100 named groups in a regular expression,
        # so only test for the exception if the limit exists.
        try:
            re.compile("".join("(?P<n{n}>{n}-)".format(n=i) for i in range(101)))
        except AssertionError:
            p = parse.compile('{:ti}' * 15)
            self.assertRaises(parse.TooManyFields, p.parse, '')


class TestSearch(unittest.TestCase):
    def test_basic(self):
        # basic search() test
        r = parse.search('a {} c', ' a b c ')
        self.assertEqual(r.fixed, ('b',))

    def test_multiline(self):
        # multiline search() test
        r = parse.search('age: {:d}\n', 'name: Rufus\nage: 42\ncolor: red\n')
        self.assertEqual(r.fixed, (42,))

    def test_pos(self):
        # basic search() test
        r = parse.search('a {} c', ' a b c ', 2)
        self.assertEqual(r, None)

    def test_no_evaluate_result(self):
        match = parse.search('age: {:d}\n', 'name: Rufus\nage: 42\ncolor: red\n', evaluate_result=False)
        r = match.evaluate_result()
        self.assertEqual(r.fixed, (42,))



class TestFindall(unittest.TestCase):
    def test_findall(self):
        # basic findall() test
        s = ''.join(r.fixed[0] for r in parse.findall(">{}<",
            "<p>some <b>bold</b> text</p>"))
        self.assertEqual(s, "some bold text")

    def test_no_evaluate_result(self):
        # basic findall() test
        s = ''.join(m.evaluate_result().fixed[0] for m in parse.findall(">{}<",
            "<p>some <b>bold</b> text</p>", evaluate_result=False))
        self.assertEqual(s, "some bold text")


class TestBugs(unittest.TestCase):
    def test_named_date_issue7(self):
        r = parse.parse('on {date:ti}', 'on 2012-09-17')
        self.assertEqual(r['date'], datetime(2012, 9, 17, 0, 0, 0))

        # fix introduced regressions
        r = parse.parse('a {:ti} b', 'a 1997-07-16T19:20 b')
        self.assertEqual(r[0], datetime(1997, 7, 16, 19, 20, 0))
        r = parse.parse('a {:ti} b', 'a 1997-07-16T19:20Z b')
        utc = parse.FixedTzOffset(0, 'UTC')
        self.assertEqual(r[0], datetime(1997, 7, 16, 19, 20, tzinfo=utc))
        r = parse.parse('a {date:ti} b', 'a 1997-07-16T19:20Z b')
        self.assertEqual(r['date'], datetime(1997, 7, 16, 19, 20, tzinfo=utc))

    def test_dotted_type_conversion_pull_8(self):
        # test pull request 8 which fixes type conversion related to dotted
        # names being applied correctly
        r = parse.parse('{a.b:d}', '1')
        self.assertEqual(r['a.b'], 1)
        r = parse.parse('{a_b:w} {a.b:d}', '1 2')
        self.assertEqual(r['a_b'], '1')
        self.assertEqual(r['a.b'], 2)

    def test_pm_overflow_issue16(self):
        r = parse.parse('Meet at {:tg}', 'Meet at 1/2/2011 12:45 PM')
        self.assertEqual(r[0], datetime(2011, 2, 1, 12, 45))

    def test_pm_handling_issue57(self):
        r = parse.parse('Meet at {:tg}', 'Meet at 1/2/2011 12:15 PM')
        self.assertEqual(r[0], datetime(2011, 2, 1, 12, 15))
        r = parse.parse('Meet at {:tg}', 'Meet at 1/2/2011 12:15 AM')
        self.assertEqual(r[0], datetime(2011, 2, 1, 0, 15))

    def test_user_type_with_group_count_issue60(self):
        @parse.with_pattern(r'((\w+))', regex_group_count=2)
        def parse_word_and_covert_to_uppercase(text):
            return text.strip().upper()

        @parse.with_pattern(r'\d+')
        def parse_number(text):
            return int(text)

        # -- CASE: Use named (OK)
        type_map = dict(Name=parse_word_and_covert_to_uppercase,
                        Number=parse_number)
        r = parse.parse('Hello {name:Name} {number:Number}',
                        'Hello Alice 42', extra_types=type_map)
        self.assertEqual(r.named, dict(name='ALICE', number=42))

        # -- CASE: Use unnamed/fixed (problematic)
        r = parse.parse('Hello {:Name} {:Number}',
                        'Hello Alice 42', extra_types=type_map)
        self.assertEqual(r[0], 'ALICE')
        self.assertEqual(r[1], 42)


# -----------------------------------------------------------------------------
# TEST SUPPORT FOR: TestParseType
# -----------------------------------------------------------------------------
class TestParseType(unittest.TestCase):

    def assert_match(self, parser, text, param_name, expected):
        result = parser.parse(text)
        self.assertEqual(result[param_name], expected)

    def assert_mismatch(self, parser, text, param_name):
        result = parser.parse(text)
        self.assertTrue(result is None)

    def assert_fixed_match(self, parser, text, expected):
        result = parser.parse(text)
        self.assertEqual(result.fixed, expected)

    def assert_fixed_mismatch(self, parser, text):
        result = parser.parse(text)
        self.assertEqual(result, None)


    def test_pattern_should_be_used(self):
        def parse_number(text):
            return int(text)
        parse_number.pattern = r"\d+"
        parse_number.name = "Number"    # For testing only.

        extra_types = {parse_number.name: parse_number}
        format = "Value is {number:Number} and..."
        parser = parse.Parser(format, extra_types)

        self.assert_match(parser, "Value is 42 and...", "number", 42)
        self.assert_match(parser, "Value is 00123 and...", "number", 123)
        self.assert_mismatch(parser, "Value is ALICE and...", "number")
        self.assert_mismatch(parser, "Value is -123 and...", "number")

    def test_pattern_should_be_used2(self):
        def parse_yesno(text):
            return parse_yesno.mapping[text.lower()]
        parse_yesno.mapping = {
            "yes": True, "no": False,
            "on": True, "off": False,
            "true": True, "false": False,
        }
        parse_yesno.pattern = r"|".join(parse_yesno.mapping.keys())
        parse_yesno.name = "YesNo"      # For testing only.

        extra_types = {parse_yesno.name: parse_yesno}
        format = "Answer: {answer:YesNo}"
        parser = parse.Parser(format, extra_types)

        # -- ENSURE: Known enum values are correctly extracted.
        for value_name, value in parse_yesno.mapping.items():
            text = "Answer: %s" % value_name
            self.assert_match(parser, text, "answer", value)

        # -- IGNORE-CASE: In parsing, calls type converter function !!!
        self.assert_match(parser, "Answer: YES", "answer", True)
        self.assert_mismatch(parser, "Answer: __YES__", "answer")

    def test_with_pattern(self):
        ab_vals = dict(a=1, b=2)

        @parse.with_pattern(r'[ab]')
        def ab(text):
            return ab_vals[text]

        parser = parse.Parser('test {result:ab}', {'ab': ab})
        self.assert_match(parser, 'test a', 'result', 1)
        self.assert_match(parser, 'test b', 'result', 2)
        self.assert_mismatch(parser, "test c", "result")

    def test_with_pattern_and_regex_group_count(self):
        # -- SPECIAL-CASE: Regex-grouping is used in user-defined type
        # NOTE: Missing or wroung regex_group_counts cause problems
        #       with parsing following params.
        @parse.with_pattern(r'(meter|kilometer)', regex_group_count=1)
        def parse_unit(text):
            return text.strip()

        @parse.with_pattern(r'\d+')
        def parse_number(text):
            return int(text)

        type_converters = dict(Number=parse_number, Unit=parse_unit)
        # -- CASE: Unnamed-params (affected)
        parser = parse.Parser('test {:Unit}-{:Number}', type_converters)
        self.assert_fixed_match(parser, 'test meter-10', ('meter', 10))
        self.assert_fixed_match(parser, 'test kilometer-20', ('kilometer', 20))
        self.assert_fixed_mismatch(parser, 'test liter-30')

        # -- CASE: Named-params (uncritical; should not be affected)
        # REASON: Named-params have additional, own grouping.
        parser2 = parse.Parser('test {unit:Unit}-{value:Number}', type_converters)
        self.assert_match(parser2, 'test meter-10', 'unit', 'meter')
        self.assert_match(parser2, 'test meter-10', 'value', 10)
        self.assert_match(parser2, 'test kilometer-20', 'unit', 'kilometer')
        self.assert_match(parser2, 'test kilometer-20', 'value', 20)
        self.assert_mismatch(parser2, 'test liter-30', 'unit')

    def test_with_pattern_and_wrong_regex_group_count_raises_error(self):
        # -- SPECIAL-CASE:
        # Regex-grouping is used in user-defined type, but wrong value is provided.
        @parse.with_pattern(r'(meter|kilometer)', regex_group_count=1)
        def parse_unit(text):
            return text.strip()

        @parse.with_pattern(r'\d+')
        def parse_number(text):
            return int(text)

        # -- CASE: Unnamed-params (affected)
        BAD_REGEX_GROUP_COUNTS_AND_ERRORS = [
            (None, ValueError),
            (0, ValueError),
            (2, IndexError),
        ]
        for bad_regex_group_count, error_class in BAD_REGEX_GROUP_COUNTS_AND_ERRORS:
            parse_unit.regex_group_count = bad_regex_group_count    # -- OVERRIDE-HERE
            type_converters = dict(Number=parse_number, Unit=parse_unit)
            parser = parse.Parser('test {:Unit}-{:Number}', type_converters)
            self.assertRaises(error_class, parser.parse, 'test meter-10')

    def test_with_pattern_and_regex_group_count_is_none(self):
        # -- CORNER-CASE: Increase code-coverage.
        data_values = dict(a=1, b=2)

        @parse.with_pattern(r'[ab]')
        def parse_data(text):
            return data_values[text]
        parse_data.regex_group_count = None     # ENFORCE: None

        # -- CASE: Unnamed-params
        parser = parse.Parser('test {:Data}', {'Data': parse_data})
        self.assert_fixed_match(parser, 'test a', (1,))
        self.assert_fixed_match(parser, 'test b', (2,))
        self.assert_fixed_mismatch(parser, 'test c')

        # -- CASE: Named-params
        parser2 = parse.Parser('test {value:Data}', {'Data': parse_data})
        self.assert_match(parser2, 'test a', 'value', 1)
        self.assert_match(parser2, 'test b', 'value', 2)
        self.assert_mismatch(parser2, 'test c', 'value')

    def test_case_sensitivity(self):
        r = parse.parse('SPAM {} SPAM', 'spam spam spam')
        self.assertEqual(r[0], 'spam')
        self.assertEqual(parse.parse('SPAM {} SPAM', 'spam spam spam', case_sensitive=True), None)

    def test_decimal_value(self):
        value = Decimal('5.5')
        str_ = 'test {}'.format(value)
        parser = parse.Parser('test {:F}')
        self.assertEqual(parser.parse(str_)[0], value)


if __name__ == '__main__':
    unittest.main()


# Copyright (c) 2011 eKit.com Inc (http://www.ekit.com/)
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

# vim: set filetype=python ts=4 sw=4 et si tw=75
