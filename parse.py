#
# $Id$
# $HeadURL$
#
'''Parse strings using a specification based on the Python format() syntax.

Anonymous (fixed-position), named and typed values are supported. Also the
alignment operators will cause whitespace (or another alignment character)
to be stripped from the value.

You may not use both fixed and named values in your format string.

The types supported in ":type" expressions are the regular expression
character group types d, D, w, W, s, S and not the string format types.

So, for example, some fixed-position parsing:

 >>> r = parse('hello {}', 'hello world')
 >>> r.fixed
 ('world', )

 >>> r = parse('hello {:d} {:w}', 'hello 12 people')
 >>> r.fixed
 ('12', 'people')

And some named parsing:

 >>> r = parse('{greeting} {name}', 'hello world')
 >>> r.named
 {'greeting': 'hello', 'name': 'world'}

 >>> r = parse('hello {^} world', 'hello  there     world')
 >>> r.fixed
 ('there', )

A ValueError will be raised if there is no match:

 >>> r = parse('hello {name:w}', 'hello 12')
 ValueError: ...

See also the unit tests at the end of the module for some more
examples.

----

This code is copyright 2009-2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
'''
__version__ = '1.0.0'

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
  (?P<fixed>{(?P<falign>[^}]?[<>^])?(:[^}]+?)?})
|
  {(?P<nalign>[^}]?[<>^])?(?P<named>\w+(:[^}]+?)?)}
)''', re.VERBOSE)


class Format(object):
    # we're an object so we can keep track of whether the user is trying to
    # specify both fixed and named args
    has_fixed = False
    has_named = False
    def replace(self, match):
        d = match.groupdict()
        if d['openbrace']: return '{{'
        if d['closebrace']: return '}}'
        align = None

        if d['fixed']:
            if self.has_named:
                raise ValueError("can't mix named and fixed")
            self.has_fixed = True
            if ':' in d['fixed']:
                x, type = d['fixed'].split(':')
                s = r'(\%s+?)' % type[:1]
            else:
                s = r'(.+?)'
            align = d['falign']

        if d['named']:
            if self.has_fixed:
                raise ValueError("can't mix named and fixed")
            self.has_named = True
            if ':' not in d['named']:
                s = r'(?P<%s>.+?)' % d['named']
            else:
                name, type = d['named'].split(':')
                s = r'(?P<%s>\%s+?)' % (name, type)
            align = d['nalign']

        if not align:
            return s

        if len(align) == 2:
            fill, align = align
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


Result = collections.namedtuple('Result', 'fixed named')


def parse(format, string):
    '''Using "format" attempt to pull values from "string".

    The return value will be an object with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If the format is invalid (usually mixing fixed-position and named values
    in the format) a ValueError will be raised.

    In the case there is no match parse() will return None.
    '''
    # first, turn the format into a regular expression
    r = PARSE_RE.sub(Format().replace, format)
    m = re.match('^' + r + '$', string)
    if m is None:
        return None
    d = m.groupdict()
    if d:
        return Result(None, d)
    else:
        return Result(m.groups(), None)


# yes, I now unit test both of the problems
class TestPattern(unittest.TestCase):
    def test_mixed(self):
        'check enforcement of fixed OR named'
        self.assertRaises(ValueError, PARSE_RE.sub, Format().replace,
            '{} {name}')

    def test_braces(self):
        'pull a simple string out of another string'
        s = PARSE_RE.sub(Format().replace, '{{ }}')
        self.assertEquals(s, '{{ }}')

    def test_fixed(self):
        'pull a simple string out of another string'
        s = PARSE_RE.sub(Format().replace, '{}')
        self.assertEquals(s, '(.+?)')
        s = PARSE_RE.sub(Format().replace, '{} {}')
        self.assertEquals(s, '(.+?) (.+?)')

    def test_typed(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(Format().replace, '{:d}')
        self.assertEquals(s, '(\d+?)')
        s = PARSE_RE.sub(Format().replace, '{:d} {:w}')
        self.assertEquals(s, '(\d+?) (\w+?)')

    def test_named(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(Format().replace, '{name}')
        self.assertEquals(s, '(?P<name>.+?)')
        s = PARSE_RE.sub(Format().replace, '{name} {other}')
        self.assertEquals(s, '(?P<name>.+?) (?P<other>.+?)')

    def test_named_typed(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(Format().replace, '{name:d}')
        self.assertEquals(s, '(?P<name>\d+?)')
        s = PARSE_RE.sub(Format().replace, '{name:d} {other:w}')
        self.assertEquals(s, '(?P<name>\d+?) (?P<other>\w+?)')

    def test_left(self):
        'skip some trailing whitespace'
        s = PARSE_RE.sub(Format().replace, '{<}')
        self.assertEquals(s, '(.+?) +')

    def test_left_fill(self):
        'skip some trailing periods'
        s = PARSE_RE.sub(Format().replace, '{.<}')
        self.assertEquals(s, '(.+?)\.+')

    def test_right(self):
        'skip some trailing whitespace'
        s = PARSE_RE.sub(Format().replace, '{>}')
        self.assertEquals(s, ' +(.+?)')

    def test_center(self):
        'skip some surrounding whitespace'
        s = PARSE_RE.sub(Format().replace, '{^}')
        self.assertEquals(s, ' +(.+?) +')


class TestParse(unittest.TestCase):
    def test_no_match(self):
        'string does not match format'
        self.assertEquals(parse('{{hello}}', 'hello'), None)

    def test_nothing(self):
        'do no actual parsing'
        r = parse('{{hello}}', '{{hello}}')
        self.assertEquals(r.fixed, ())
        self.assertEquals(r.named, None)

    def test_fixed(self):
        'pull a fixed value out of string'
        r = parse('hello {}', 'hello world')
        self.assertEquals(r.fixed, ('world', ))

    def test_left(self):
        'pull left-aligned text out of string'
        r = parse('{<} world', 'hello       world')
        self.assertEquals(r.fixed, ('hello', ))

    def test_right(self):
        'pull right-aligned text out of string'
        r = parse('hello {>}', 'hello       world')
        self.assertEquals(r.fixed, ('world', ))

    def test_center(self):
        'pull right-aligned text out of string'
        r = parse('hello {^} world', 'hello  there     world')
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

    def test_named_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {number:d} {things}', 'hello 12 people')
        self.assertEquals(r.named, dict(number='12', things='people'))


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

