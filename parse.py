#
# $Id$
# $HeadURL$
#
'''Parse strings using a specification based on the Python format() syntax.

   parse() is the opposite of format()

The `Format String Syntax`_ is supported with anonymous (fixed-position),
named and formatted fields are supported::

   {[field name]:[format spec]}

Field names must be a single Python identifier word. No attributes or
element indexes are supported (as they would make no sense.)

Numbered fields are also not supported: the result of parsing will include
the parsed fields in the order they are parsed.

The conversion of fields to types other than strings is not yet supported.

Some simple parse() format string examples:

>>> parse("Bring me a {}", "Bring me a shrubbery")
<Result ('shrubbery',) {}>
>>> r = parse("The {} who say {}", "The knights who say Ni!")
>>> print r
<Result ('knights', 'Ni!') {}>
>>> print r.fixed
('knights', 'Ni!')
>>> r = parse("Bring out the holy {item}", "Bring out the holy hand grenade")
>>> print r
<Result () {'item': 'hand grenade'}>
>>> print r.named
{'item': 'hand grenade'}

Most of the `Format Specification Mini-Language`_ is supported::

   [[fill]align][sign][#][0][width][,][.precision][type]

The align operators will cause spaces (or specified fill character)
to be stripped from the value. The alignment character "=" is not yet
supported.

The comma "," separator is not yet supported.

The types supported are the not the format() types but rather some of
those types b, o, h, x, X and also regular expression character group types
d, D, w, W, s, S and not the string format types. The format() types n, f,
F, e, E, g and G are not yet supported.

===== ==========================================
Type  Characters Matched
===== ==========================================
 w    Letters and underscore
 W    Non-letter and underscore
 s    Whitespace
 S    Non-whitespace
 d    Digits (effectively integer numbers)
 D    Non-digit
 b    Binary numbers
 o    Octal numbers
 h    Hexadecimal numbers (lower and upper case)
 x    Lower-case hexadecimal numbers
 X    Upper-case hexadecimal numbers
===== ==========================================

Do remember though that most often a straight type-less {} will suffice
where a more complex type specification might have been used.

So, for example, some typed parsing, and None resulting if the typing
does not match:

>>> parse('Hello {:d} {:w}', 'Hello 12 people')
<Result ('12', 'people') {}>
>>> print parse('Hello {:d} {:w}', 'Hello twelve people')
None

And messing about with alignment:

>>> parse('hello {:<} world', 'hello there     world')
<Result ('there',) {}>
>>> parse('hello {:^} world', 'hello    there     world')
<Result ('there',) {}>

Note that the "center" alignment does not test to make sure the value is
actually centered. It just strips leading and trailing whitespace.

See also the unit tests at the end of the module for some more
examples. Run the tests with "python -m parse".

.. _`Format String Syntax`: http://docs.python.org/library/string.html#format-string-syntax
.. _`Format Specification Mini-Language`: http://docs.python.org/library/string.html#format-specification-mini-language

----

**Version history (in brief)**:

- 1.1.1 documentation improvements
- 1.1.0 implemented more of the `Format Specification Mini-Language`_
  and removed the restriction on mixing fixed-position and named fields
- 1.0.0 initial release

This code is copyright 2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
'''
__version__ = '1.1.1'

import re
import unittest
import collections


# yes, I now have two problems
PARSE_RE = re.compile('''
(
  (?P<openbrace>{{)
|
  (?P<closebrace>}})
|
  (?P<fixed>{(:[^}]+?)?})
|
  {(?P<named>\w+(:[^}]+?)?)}
)''', re.VERBOSE)


# three problems?
FORMAT_RE = re.compile('''
    (?P<align>(?P<fill>[^}])?[<>^])?
    (?P<sign>[-+ ])?
    (?P<prefix>\#)?
    (?P<width>(?P<zero>0)?[1-9]\d*)?
    (\.(?P<precision>\d+))?
    (?P<type>[bohxXwWdDsS])?
''', re.VERBOSE)


class Result(object):
    def __init__(self):
        self._fixed_args = []
        self._groups = 0
        self.fixed = ()
        self.named = {}

    def __repr__(self):
        return '<Result %r %r>' % (self.fixed, self.named)

    @classmethod
    def parse(cls, format, string):
        o = cls()
        # first, turn the format into a regular expression
        r = PARSE_RE.sub(o.replace, format)
        m = re.match('^' + r + '$', string)
        if m is None:
            return None

        l = m.groups()

        o.named = m.groupdict()
        o.fixed = tuple(l[n] for n in o._fixed_args)

        return o

    def replace(self, match):
        d = match.groupdict()
        if d['openbrace']: return '{'
        if d['closebrace']: return '}'

        format = ''

        #print 'PARSE', d

        if d['fixed']:
            self._fixed_args.append(self._groups)
            wrap = '(%s)'
            if ':' in d['fixed']:
                format = d['fixed'][2:-1]
        elif d['named']:
            if ':' in d['named']:
                name, format = d['named'].split(':')
            else:
                name = d['named']
            wrap = '(?P<%s>%%s)' % name
        else:
            raise ValueError('format not recognised')

        self._groups += 1

        if not format:
            return wrap % '.+?'

        m = FORMAT_RE.match(format)
        if m is None:
            raise ValueError('format %r not recognised' % format)

        d = m.groupdict()
        #print 'FORMAT', d

        if d['type'] == 'o':
            s = '[0-7]'
        elif d['type'] == 'b':
            s = '[01]'
        elif d['type'] == 'h':
            s = '[0-9a-fA-F]'
        elif d['type'] == 'x':
            s = '[0-9a-f]'
        elif d['type'] == 'X':
            s = '[0-9A-F]'
        elif d['type']:
            s = r'\%s' % d['type']
        else:
            s = '.'

        # TODO: number types still to support:
        # n    Number (with number separator characters)
        # f    Floating-point numbers
        # e    Exponent notation
        # E    Exponent notation with upper-case E
        # g    General number format with added nan, inf and -inf
        # G    General number format with upper-case E, NAN, INF and -INF

        if d['type'] and d['type'] in 'dobhxX':
            if d['prefix']:
                if d['type'] == 'b':
                    s = '0b' + s
                elif d['type'] == 'o':
                    s = '0o' + s
                elif d['type'] in 'hxX':
                    s = '0x' + s
                else:
                    raise ValueError('prefix # not compatible with type %s' %
                        d['type'])
            if not d['sign']:
                # default sign handling
                s = r'-?' + s
            elif d['sign'] == '+':
                s = r'[-+]?' + s
            elif d['sign'] == '-':
                s = r'-?' + s
            elif d['sign'] == ' ':
                s = r'[- ]?' + s
            else:
                raise ValueError('sign in format "%s" unrecognised' % d['sign'])
        else:
            if d['prefix']:
                raise ValueError('prefix # in format must accompany numeric type')
            if d['sign']:
                raise ValueError('sign in format must accompany "d" type')

        if d['width']:
            if d['zero']:
                s = s + '{%s}' % d['width'][1:]
            else:
                s = s + '{%s}' % d['width']
        else:
            s = s + '+?'

        s = wrap % s

        if d['zero']:
            s = '0*' + s

        # TODO handle precision
        #(\.(?P<precision>\d+))?

        # TODO support '='
        align = d['align']
        fill = d['fill']
        if fill:
            align = align[1]
        else:
            fill = ' '

        if fill in '.\+?*[](){}^$':
            fill = '\\' + fill
        if align == '<':
            s = '%s%s+' % (s, fill)
        elif align == '>':
            s = '%s+%s' % (fill, s)
        elif align == '^':
            s = '%s+%s%s+' % (fill, s, fill)
        return s


def parse(format, string):
    '''Using "format" attempt to pull values from "string".

    The return value will be an object with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If the format is invalid a ValueError will be raised.

    In the case there is no match parse() will return None.
    '''
    return Result().parse(format, string)


# yes, I now unit test both of the problems
class TestPattern(unittest.TestCase):
    def test_braces(self):
        'pull a simple string out of another string'
        s = PARSE_RE.sub(Result().replace, '{{ }}')
        self.assertEquals(s, '{ }')

    def test_fixed(self):
        'pull a simple string out of another string'
        s = PARSE_RE.sub(Result().replace, '{}')
        self.assertEquals(s, '(.+?)')
        s = PARSE_RE.sub(Result().replace, '{} {}')
        self.assertEquals(s, '(.+?) (.+?)')

    def test_typed(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(Result().replace, '{:d}')
        self.assertEquals(s, '(-?\d+?)')
        s = PARSE_RE.sub(Result().replace, '{:d} {:w}')
        self.assertEquals(s, '(-?\d+?) (\w+?)')

    def test_named(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(Result().replace, '{name}')
        self.assertEquals(s, '(?P<name>.+?)')
        s = PARSE_RE.sub(Result().replace, '{name} {other}')
        self.assertEquals(s, '(?P<name>.+?) (?P<other>.+?)')

    def test_named_typed(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(Result().replace, '{name:d}')
        self.assertEquals(s, '(?P<name>-?\d+?)')
        s = PARSE_RE.sub(Result().replace, '{name:d} {other:w}')
        self.assertEquals(s, '(?P<name>-?\d+?) (?P<other>\w+?)')

    def test_beaker(self):
        'skip some trailing whitespace'
        s = PARSE_RE.sub(Result().replace, '{:<}')
        self.assertEquals(s, '(.+?) +')

    def test_left_fill(self):
        'skip some trailing periods'
        s = PARSE_RE.sub(Result().replace, '{:.<}')
        self.assertEquals(s, '(.+?)\.+')

    def test_bird(self):
        'skip some trailing whitespace'
        s = PARSE_RE.sub(Result().replace, '{:>}')
        self.assertEquals(s, ' +(.+?)')

    def test_center(self):
        'skip some surrounding whitespace'
        s = PARSE_RE.sub(Result().replace, '{:^}')
        self.assertEquals(s, ' +(.+?) +')

    def test_format(self):
        def _(fmt, matches):
            m = FORMAT_RE.match(fmt)
            self.assertNotEquals(m, None,
                'FORMAT_RE failed to parse %r' % fmt)
            d = m.groupdict()
            for k in matches:
                self.assertEquals(d.get(k), matches[k],
                    'm["%s"]=%r, expect %r' % (k, d.get(k), matches[k]))

        for t in 'obhdDwWsS':
            _(t, dict(type=t))
            _('10'+t, dict(type=t, width='10'))
        _('05d', dict(type='d', width='05', zero='0'))
        _('#d', dict(type='d', prefix='#'))
        _('<', dict(align='<'))
        _('.<', dict(align='.<', fill='.'))
        _('>', dict(align='>'))
        _('.>', dict(align='.>', fill='.'))
        _('^', dict(align='^'))
        _('.^', dict(align='.^', fill='.'))
        _('d', dict(type='d'))
        _('-d', dict(type='d', sign='-'))
        _('+d', dict(type='d', sign='+'))
        _(' d', dict(type='d', sign=' '))

        _('.^+#010d', dict(type='d', width='010', align='.^', fill='.', prefix='#',
            sign='+', zero='0'))

        #(\.(?P<precision>\d+))?

class TestParse(unittest.TestCase):
    def test_no_match(self):
        'string does not match format'
        self.assertEquals(parse('{{hello}}', 'hello'), None)

    def test_nothing(self):
        'do no actual parsing'
        r = parse('{{hello}}', '{hello}')
        self.assertEquals(r.fixed, ())
        self.assertEquals(r.named, {})

    def test_fixed(self):
        'pull a fixed value out of string'
        r = parse('hello {}', 'hello world')
        self.assertEquals(r.fixed, ('world', ))

    def test_left(self):
        'pull left-aligned text out of string'
        r = parse('{:<} world', 'hello       world')
        self.assertEquals(r.fixed, ('hello', ))

    def test_right(self):
        'pull right-aligned text out of string'
        r = parse('hello {:>}', 'hello       world')
        self.assertEquals(r.fixed, ('world', ))

    def test_center(self):
        'pull right-aligned text out of string'
        r = parse('hello {:^} world', 'hello  there     world')
        self.assertEquals(r.fixed, ('there', ))

    def test_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {:d} {:w}', 'hello 12 people')
        self.assertEquals(r.fixed, ('12', 'people'))

    def test_typed_fail(self):
        'pull a named, typed values out of string'
        self.assertEquals(parse('hello {:d} {:w}', 'hello people 12'), None)

    def test_named(self):
        'pull a named value out of string'
        r = parse('hello {name}', 'hello world')
        self.assertEquals(r.named, {'name': 'world'})

    def test_mixed(self):
        'pull a fixed and named values out of string'
        r = parse('hello {} {name} {} {spam}', 'hello world and other beings')
        self.assertEquals(r.fixed, ('world', 'other'))
        self.assertEquals(r.named, dict(name='and', spam='beings'))

    def test_named_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {number:d} {things}', 'hello 12 people')
        self.assertEquals(r.named, dict(number='12', things='people'))

    def test_named_aligned_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {number:<d} {things}', 'hello 12      people')
        self.assertEquals(r.named, dict(number='12', things='people'))
        r = parse('hello {number:>d} {things}', 'hello      12 people')
        self.assertEquals(r.named, dict(number='12', things='people'))
        r = parse('hello {number:^d} {things}', 'hello      12      people')
        self.assertEquals(r.named, dict(number='12', things='people'))

    def test_numbers(self):
        'pull a numbers out of a string'
        def y(fmt, s, e):
            r = parse(fmt, s)
            if r is None: self.fail('%r did not match %r' % (fmt, s))
            self.assertEquals(r.fixed[0], e,
                '%r found %r in %r, not %r' % (fmt, r.fixed[0], s, e))
        def n(fmt, s, e):
            if parse(fmt, s) is not None:
                self.fail('%r matched %r' % (fmt, s))
        y('a {:d} b', 'a 12 b', '12')
        y('a {:d} b', 'a -12 b', '-12')
        n('a {:d} b', 'a +12 b', None)
        y('a {:-d} b', 'a -12 b', '-12')
        n('a {:-d} b', 'a +12 b', None)
        y('a {:+d} b', 'a -12 b', '-12')
        y('a {:+d} b', 'a +12 b', '+12')
        y('a {: d} b', 'a -12 b', '-12')
        y('a {: d} b', 'a  12 b', ' 12')
        n('a {: d} b', 'a +12 b', None)

        y('a {:b} b', 'a 101101 b', '101101')
        y('a {:#b} b', 'a 0b101101 b', '0b101101')
        y('a {:o} b', 'a 12345670 b', '12345670')
        y('a {:#o} b', 'a 0o12345670 b', '0o12345670')
        y('a {:h} b', 'a 1234567890abcdef b', '1234567890abcdef')
        y('a {:h} b', 'a 1234567890ABCDEF b', '1234567890ABCDEF')
        y('a {:#h} b', 'a 0x1234567890abcdef b', '0x1234567890abcdef')
        y('a {:#h} b', 'a 0x1234567890ABCDEF b', '0x1234567890ABCDEF')
        y('a {:x} b', 'a 1234567890abcdef b', '1234567890abcdef')
        y('a {:X} b', 'a 1234567890ABCDEF b', '1234567890ABCDEF')
        y('a {:#x} b', 'a 0x1234567890abcdef b', '0x1234567890abcdef')
        y('a {:#X} b', 'a 0x1234567890ABCDEF b', '0x1234567890ABCDEF')

        y('a {:05d} b', 'a 00001 b', '00001')

        # TODO this should pass
        # y('a {:05d} b', 'a 0000001 b', None)

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
