#
# $Id$
# $HeadURL$
#
'''Parse strings using a specification based on the Python format() syntax.

   parse() is the opposite of format()

Basic usage:

>>> from parse import *            # only exports parse() and compile()
>>> parse("It's {}, I love it!", "It's spam, I love it!")
<Result ('spam',) {}>
>>> p = compile("It's {}, I love it!")
>>> print p
<Parser "It's {}, I love it!">
>>> p.parse("It's spam, I love it!")
<Result ('spam',) {}>


Format Syntax
-------------

A basic version of the `Format String Syntax`_ is supported with anonymous
(fixed-position), named and formatted fields::

   {[field name]:[format spec]}

Field names must be a single Python identifier word. No attributes or
element indexes are supported (as they would make no sense.)

Numbered fields are also not supported: the result of parsing will include
the parsed fields in the order they are parsed.

The conversion of fields to types other than strings is done based on the
type in the format specification, which mirrors the format() behaviour.
There are no "!" field conversions like format() has.

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

Format Specification
--------------------

Do remember that most often a straight format-less {} will suffice
where a more complex format specification might have been used.

Most of the `Format Specification Mini-Language`_ is supported::

   [[fill]align][sign][0][width][type]

The align operators will cause spaces (or specified fill character)
to be stripped from the value. Similarly width is not enforced; it
just indicates there may be whitespace or "0"s to strip.

The "#" format character is handled automatically by b, o and x - that
is: if there is a "0b", "0o" or "0x" prefix respectively, it's ignored.

The types supported are a slightly different mix to the format() types.
Some format() types come directly over: d, n, f, e, b, o and x.
In addition some regular expression character group types
D, w, W, s and S are also available.

The "e" and "g" types are case-insensitive so there is not need for
the "E" or "G" types.

The format() type % is not yet supported.

===== =========================================== ========
Type  Characters Matched                          Output
===== =========================================== ========
 w    Letters and underscore                      str
 W    Non-letter and underscore                   str
 s    Whitespace                                  str
 S    Non-whitespace                              str
 d    Digits (effectively integer numbers)        int
 D    Non-digit                                   str
 n    Numbers with thousands separators (, or .)  int
 f    Fixed-point numbers                         float
 e    Floating-point numbers with exponent        float
      e.g. 1.1e-10, NAN (all case insensitive)
 g    General number format (either d, f or e)    float
 b    Binary numbers                              int
 o    Octal numbers                               int
 x    Hexadecimal numbers (lower and upper case)  int
 ti   ISO 8601 format date/time                   datetime
      e.g. 1972-01-20T10:21:36Z
 te   RFC2822 e-mail format date/time             datetime
      e.g. Mon, 20 Jan 1972 10:21:36 +1000
 tg   Global (day/month) format date/time         datetime
      e.g. 20/1/1972 10:21:36 AM +1:00
 ta   US (month/day) format date/time             datetime
      e.g. 1/20/1972 10:21:36 PM +10:30
 tc   ctime() format date/time                    datetime
      e.g. Sun Sep 16 01:03:52 1973
 th   HTTP log format date/time                   datetime
      e.g. 21/Nov/2011:00:07:11 +0000
 tt   Time                                        time
      e.g. 10:21:36 PM -5:30
===== =========================================== ========

So, for example, some typed parsing, and None resulting if the typing
does not match:

>>> parse('Our {:d} {:w} are...', 'Our 3 weapons are...')
<Result (3, 'weapons') {}>
>>> parse('Our {:d} {:w} are...', 'Our three weapons are...')
None

And messing about with alignment:

>>> parse('with {:>} herring', 'with     a herring')
<Result ('a',) {}>
>>> parse('spam {:^} spam', 'spam    lovely     spam')
<Result ('lovely',) {}>

Note that the "center" alignment does not test to make sure the value is
actually centered. It just strips leading and trailing whitespace.

See also the unit tests at the end of the module for some more
examples. Run the tests with "python -m parse".

Some notes for the date and time types:

- the presence of the time part is optional (including ISO 8601, starting
  at the "T"). A full datetime object will always be returned; the time
  will be set to 00:00:00.
- except in ISO 8601 the day and month digits may be 0-padded
- the separator for the ta and tg formats may be "-" or "/"
- named months (abbreviations or full names) may be used in the ta and tg
  formats
- as per RFC 2822 the e-mail format may omit the day (and comma), and the
  seconds but nothing else
- hours greater than 12 will be happily accepted
- the AM/PM are optional, and if PM is found then 12 hours will be added
  to the datetime object's hours amount - even if the hour is greater
  than 12 (for consistency.)
- except in ISO 8601 and e-mail format the timezone is optional
- when a seconds amount is present in the input fractions will be parsed
- named timezones are not handled yet

.. _`Format String Syntax`: http://docs.python.org/library/string.html#format-string-syntax
.. _`Format Specification Mini-Language`: http://docs.python.org/library/string.html#format-specification-mini-language


Result Objects
--------------

The result of a ``parse()`` operation is either ``None`` (no match) or a
``Result`` instance.

The ``Result`` instance has three attributes:

fixed
   A tuple of the fixed-position, anonymous fields extracted from the input.
named
   A dictionary of the named fields extracted from the input.
spans
   A dictionary mapping the names and fixed position indices matched to a
   2-tuple slice range of where the match occurred in the input.
   The span does not include any stripped padding (alignment or width).

----

**Version history (in brief)**:

- 1.1.7 Python 3 compatibility tweaks (2.5 to 2.7 and 3.2 are supported).
- 1.1.6 add "e" and "g" field types; removed redundant "h" and "X";
  removed need for explicit "#".
- 1.1.5 accept textual dates in more places; Result now holds match span
  positions.
- 1.1.4 fixes to some int type conversion; implemented "=" alignment; added
  date/time parsing with a variety of formats handled.
- 1.1.3 type conversion is automatic based on specified field types. Also added
  "f" and "n" types.
- 1.1.2 refactored, added compile() and limited ``from parse import *``
- 1.1.1 documentation improvements
- 1.1.0 implemented more of the `Format Specification Mini-Language`_
  and removed the restriction on mixing fixed-position and named fields
- 1.0.0 initial release

This code is copyright 2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
'''
__version__ = '1.1.7'

import re
import unittest
from datetime import datetime, time, tzinfo, timedelta

__all__ = 'parse compile'.split()


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
    (?P<align>(?P<fill>[^}])?[<>^=])?
    (?P<sign>[-+ ])?
    (?P<width>(?P<zero>0)?[1-9]\d*)?
    (\.(?P<precision>\d+))?
    (?P<type>([nboxfegwWdDsS]|t[ieahgct]))?
''', re.VERBOSE)

def int_convert(base):
    '''Convert a string to an integer.

    The string may start with a sign.

    It may be of a base other than 10.

    It may also have other non-numeric characters that we can ignore.
    '''
    CHARS = '0123456789abcdefghijklmnopqrstuvwxyz'
    def f(string, match, base=base):
        if string[0] == '-':
            sign = -1
        else:
            sign = 1

        chars = CHARS[:base]
        string = re.sub('[^%s]' % chars, '', string.lower())
        return sign * int(string, base)
    return f


class FixedTzOffset(tzinfo):
    """Fixed offset in minutes east from UTC.
    """
    def __init__(self, offset, name):
        self._offset = timedelta(minutes = offset)
        self._name = name

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self._name, self._offset)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self._name

    def dst(self, dt):
        return ZERO

    def __eq__(self, other):
        return self._name == other._name and self._offset == other._offset

MONTHS_MAP = dict(
    Jan=1, January=1,
    Feb=2, February=2,
    Mar=3, March=3,
    Apr=4, April=4,
    May=5,
    Jun=6, June=6,
    Jul=7, July=7,
    Aug=8, August=8,
    Sep=9, September=9,
    Oct=10, October=10,
    Nov=11, November=11,
    Dec=12, December=12
)
DAYS_PAT = '(Mon|Tue|Wed|Thu|Fri|Sat|Sun)'
MONTHS_PAT = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
ALL_MONTHS_PAT = '(%s)' % '|'.join(MONTHS_MAP)
TIME_PAT = r'(?P<hms>\d{1,2}:\d{1,2}(:\d{1,2}(\.\d+)?)?)'
AM_PAT = r'(?P<am>\s+[AP]M)'
TZ_PAT = r'(?P<tz>\s+[-+]\d\d:?\d\d)'

def time_convert(string, match):
    return date_convert(string, match, True)

def date_convert(string, match, time_only=False):
    '''Convert the incoming string containing some date / time info into a
    datetime instance.
    '''
    gd = match.groupdict()
    if not time_only:
        if gd.get('ymd'):
            y, m, d = re.split('[-/\s]', gd['ymd'])
        elif gd.get('mdy'):
            m, d, y = re.split('[-/\s]', gd['mdy'])
        elif gd.get('dmy'):
            d, m, y = re.split('[-/\s]', gd['dmy'])
        elif gd.get('d'):
            d = gd['d']
            m = gd['m']
            y = gd['y']
        else:
            raise ValueError('oops, got no date format in %r' % (gd, ))
        y = int(y)
        if m.isdigit():
            m = int(m)
        else:
            m = MONTHS_MAP[m]
        d = int(d)

    H = M = S = u = 0
    if gd['hms']:
        t = gd['hms'].split(':')
        if len(t) == 2:
            H, M = t
        else:
            H, M, S = t
            if '.' in S:
                S, u = S.split('.')
                u = int(float('.' + u) * 1000000)
            S = int(S)
        H = int(H)
        M = int(M)

    am = gd.get('am')
    if am and am.strip() == 'PM':
        H += 12

    tz = gd.get('tz')
    if tz == 'Z':
        tz = FixedTzOffset(0, 'UTC')
    elif tz:
        tz = tz.strip()
        if tz.isupper():
            # TODO use the awesome python TZ module?
            TODO
        else:
            sign = tz[0]
            if ':' in tz:
                tzh, tzm = tz[1:].split(':')
            else:
                tzh, tzm = tz[1:3], tz[3:5]
            tz = FixedTzOffset(int(tzm) + int(tzh) * 60, tz)

    if time_only:
        d = time(H, M, S, u, tzinfo=tz)
    else:
        d = datetime(y, m, d, H, M, S, u, tzinfo=tz)

    return d


class Parser(object):
    def __init__(self, format):
        self._fixed_args = []
        self._groups = 0
        self._format = format
        self._type_conversions = {}
        self._expression = '^%s$' % PARSE_RE.sub(self.replace, format)
        self._re = re.compile(self._expression, re.IGNORECASE|re.DOTALL)

    def __repr__(self):
        if len(self._format) > 20:
            return '<%s %r>' % (self.__class__.__name__, self._format[:17] + '...')
        return '<%s %r>' % (self.__class__.__name__, self._format)

    def parse(self, string):
        m = self._re.match(string)
        if m is None:
            return None
        l = list(m.groups())
        for n in self._fixed_args:
            if n in self._type_conversions:
                l[n] = self._type_conversions[n](l[n], m)
        named = m.groupdict()
        spans = dict((n, m.span(n)) for n in named)
        for k in named:
            if k in self._type_conversions:
                named[k] = self._type_conversions[k](named[k], m)
        fixed = tuple(l[n] for n in self._fixed_args)
        spans.update((i, m.span(n+1)) for i, n in enumerate(self._fixed_args))
        return Result(fixed, named, spans)

    def replace(self, match):
        d = match.groupdict()
        if d['openbrace']: return '{'
        if d['closebrace']: return '}'

        format = ''

        if d['fixed']:
            self._fixed_args.append(self._groups)
            wrap = '(%s)'
            if ':' in d['fixed']:
                format = d['fixed'][2:-1]
            group = self._groups
        elif d['named']:
            if ':' in d['named']:
                name, format = d['named'].split(':')
            else:
                name = d['named']
            group = name
            wrap = '(?P<%s>%%s)' % name
        else:
            raise ValueError('format not recognised')

        self._groups += 1

        # simplest case: a bare {}
        if not format:
            return wrap % '.+?'

        # now figure out the format
        m = FORMAT_RE.match(format)
        if m is None:
            raise ValueError('format %r not recognised' % format)

        d = m.groupdict()

        prefix = False

        # figure type conversions, if any
        if d['type'] == 'n':
            s = '\d{1,3}([,.]\d{3})*'
            self._type_conversions[group] = int_convert(10)
        elif d['type'] == 'o':
            prefix = True
            s = '[0-7]+'
            self._type_conversions[group] = int_convert(8)
        elif d['type'] == 'b':
            prefix = True
            s = '[01]+'
            self._type_conversions[group] = int_convert(2)
        elif d['type'] == 'x':
            prefix = True
            s = '[0-9a-fA-F]+'
            self._type_conversions[group] = int_convert(16)
        elif d['type'] == 'f':
            s = r'\d+\.\d+'
            self._type_conversions[group] = lambda s, m: float(s)
        elif d['type'] == 'e':
            s = r'\d+\.\d+[eE][-+]?\d+|nan|NAN|[-+]?inf|[-+]?INF'
            self._type_conversions[group] = lambda s, m: float(s)
        elif d['type'] == 'g':
            s = r'\d+(\.\d+)?([eE][-+]?\d+)?|nan|NAN|[-+]?inf|[-+]?INF'
            self._type_conversions[group] = lambda s, m: float(s)
        elif d['type'] == 'd':
            s = r'\d+'
            self._type_conversions[group] = int_convert(10)
        elif d['type'] == 'ti':
            s = r'(?P<ymd>\d{4}-\d\d-\d\d)((\s+|T)%s)?(?P<tz>Z|[-+]\d\d:\d\d)?' % (TIME_PAT,)
            self._type_conversions[group] = date_convert
        elif d['type'] == 'ta':
            s = r'(?P<mdy>(\d{1,2}|%s)[-/]\d{1,2}[-/]\d{4})(\s+%s)?%s?%s?' % (ALL_MONTHS_PAT, TIME_PAT, AM_PAT, TZ_PAT)
            self._type_conversions[group] = date_convert
        elif d['type'] == 'tg':
            s = r'(?P<dmy>\d{1,2}[-/](\d{1,2}|%s)[-/]\d{4})(\s+%s)?%s?%s?' % (ALL_MONTHS_PAT, TIME_PAT, AM_PAT, TZ_PAT)
            self._type_conversions[group] = date_convert
        elif d['type'] == 'te':
            # this will allow microseconds through if they're present, but meh
            s = r'(%s,\s+)?(?P<dmy>\d{1,2}\s+%s\s+\d{4})\s+%s%s' % (DAYS_PAT, MONTHS_PAT, TIME_PAT, TZ_PAT)
            self._type_conversions[group] = date_convert
        elif d['type'] == 'th':
            # slight flexibility here from the stock Apache format
            s = r'(?P<dmy>\d{1,2}[-/]%s[-/]\d{4}):%s%s' % (MONTHS_PAT, TIME_PAT, TZ_PAT)
            self._type_conversions[group] = date_convert
        elif d['type'] == 'tc':
            s = r'(%s)\s+(?P<m>%s)\s+(?P<d>\d{1,2})\s+%s\s+(?P<y>\d{4})' % (DAYS_PAT, MONTHS_PAT, TIME_PAT)
            self._type_conversions[group] = date_convert
        elif d['type'] == 'tt':
            s = r'%s?%s?%s?' % (TIME_PAT, AM_PAT, TZ_PAT)
            self._type_conversions[group] = time_convert
        elif d['type']:
            s = r'\%s+' % d['type']
        else:
            s = '.+?'

        # figure the alignment and fill parameters
        align = d['align']
        fill = d['fill']
        if fill:
            align = align[1]
        else:
            fill = ' '

        is_numeric = d['type'] and d['type'] in 'nfdobhxX'

        # handle some numeric-specific things like prefix and sign
        if is_numeric:
            if prefix:
                if d['type'] == 'b':
                    s = '(0b)?' + s
                elif d['type'] == 'o':
                    s = '(0o)?' + s
                elif d['type'] in 'hxX':
                    s = '(0x)?' + s

            # prefix with something (align "=" trumps zero)
            if align == '=':
                # special case - align "=" acts like the zero above but with
                # configurable fill defaulting to "0"
                if not d['fill']:
                    fill = '0'
                s = '%s*' % fill + s
            elif d['zero']:
                s = '0*' + s

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
            if d['sign']:
                raise ValueError('sign in format must accompany "d" type')

        # Place into a group now - this captures the value we want to keep.
        # Everything else from now is just padding to be stripped off
        s = wrap % s

        if d['width']:
            # all we really care about is that if the format originally
            # specified a width then there will probably be padding - without an
            # explicit alignment that'll mean right alignment with spaces
            # padding
            if not align:
                align = '>'

        if fill in '.\+?*[](){}^$':
            fill = '\\' + fill

        # align "=" has been handled
        if align == '<':
            s = '%s%s*' % (s, fill)
        elif align == '>':
            s = '%s*%s' % (fill, s)
        elif align == '^':
            s = '%s*%s%s*' % (fill, s, fill)
        return s


class Result(object):
    def __init__(self, fixed, named, spans):
        self.fixed = fixed
        self.named = named
        self.spans = spans

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.fixed,
            self.named)


def parse(format, string):
    '''Using "format" attempt to pull values from "string".

    The return value will be an object with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If the format is invalid a ValueError will be raised.

    In the case there is no match parse() will return None.
    '''
    return Parser(format).parse(string)


def compile(format):
    '''Create a Parser instance to parse "format".

    The resultant Parser has a method .parse(string) which
    behaves in the same manner as parse(format, string).

    Use this function if you intend to parse many strings
    with the same format.
    '''
    return Parser(format)


# yes, I now unit test both of the problems
class TestPattern(unittest.TestCase):
    def setUp(self):
        self.p = Parser('')

    def test_braces(self):
        'pull a simple string out of another string'
        s = PARSE_RE.sub(self.p.replace, '{{ }}')
        self.assertEqual(s, '{ }')

    def test_fixed(self):
        'pull a simple string out of another string'
        s = PARSE_RE.sub(self.p.replace, '{}')
        self.assertEqual(s, '(.+?)')
        s = PARSE_RE.sub(self.p.replace, '{} {}')
        self.assertEqual(s, '(.+?) (.+?)')

    def test_typed(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(self.p.replace, '{:d}')
        self.assertEqual(s, '(-?\d+)')
        s = PARSE_RE.sub(self.p.replace, '{:d} {:w}')
        self.assertEqual(s, '(-?\d+) (\w+)')

    def test_named(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(self.p.replace, '{name}')
        self.assertEqual(s, '(?P<name>.+?)')
        s = PARSE_RE.sub(self.p.replace, '{name} {other}')
        self.assertEqual(s, '(?P<name>.+?) (?P<other>.+?)')

    def test_named_typed(self):
        'pull a named string out of another string'
        s = PARSE_RE.sub(self.p.replace, '{name:d}')
        self.assertEqual(s, '(?P<name>-?\d+)')
        s = PARSE_RE.sub(self.p.replace, '{name:d} {other:w}')
        self.assertEqual(s, '(?P<name>-?\d+) (?P<other>\w+)')

    def test_beaker(self):
        'skip some trailing whitespace'
        s = PARSE_RE.sub(self.p.replace, '{:<}')
        self.assertEqual(s, '(.+?) *')

    def test_left_fill(self):
        'skip some trailing periods'
        s = PARSE_RE.sub(self.p.replace, '{:.<}')
        self.assertEqual(s, '(.+?)\.*')

    def test_bird(self):
        'skip some trailing whitespace'
        s = PARSE_RE.sub(self.p.replace, '{:>}')
        self.assertEqual(s, ' *(.+?)')

    def test_center(self):
        'skip some surrounding whitespace'
        s = PARSE_RE.sub(self.p.replace, '{:^}')
        self.assertEqual(s, ' *(.+?) *')

    def test_float(self):
        'skip test float expression generation'
        _ = lambda s: PARSE_RE.sub(self.p.replace, s)
        self.assertEqual(_('{:f}'), '(-?\d+\.\d+)')
        self.assertEqual(_('{:+f}'), '([-+]?\d+\.\d+)')

    def test_number_commas(self):
        'skip number with commas generation'
        _ = lambda s: PARSE_RE.sub(self.p.replace, s)
        self.assertEqual(_('{:n}'), '(-?\\d{1,3}([,.]\\d{3})*)')
        self.assertEqual(_('{:+n}'), '([-+]?\\d{1,3}([,.]\\d{3})*)')

    def test_format(self):
        def _(fmt, matches):
            m = FORMAT_RE.match(fmt)
            self.assertNotEqual(m, None,
                'FORMAT_RE failed to parse %r' % fmt)
            d = m.groupdict()
            for k in matches:
                self.assertEqual(d.get(k), matches[k],
                    'm["%s"]=%r, expect %r' % (k, d.get(k), matches[k]))

        for t in 'obxegfdDwWsS':
            _(t, dict(type=t))
            _('10'+t, dict(type=t, width='10'))
        _('05d', dict(type='d', width='05', zero='0'))
        _('<', dict(align='<'))
        _('.<', dict(align='.<', fill='.'))
        _('>', dict(align='>'))
        _('.>', dict(align='.>', fill='.'))
        _('^', dict(align='^'))
        _('.^', dict(align='.^', fill='.'))
        _('x=d', dict(type='d', align='x=', fill='x'))
        _('d', dict(type='d'))
        _('-d', dict(type='d', sign='-'))
        _('+d', dict(type='d', sign='+'))
        _(' d', dict(type='d', sign=' '))
        _('ti', dict(type='ti'))

        _('.^+010d', dict(type='d', width='010', align='.^', fill='.',
            sign='+', zero='0'))


class TestParse(unittest.TestCase):
    def test_no_match(self):
        'string does not match format'
        self.assertEqual(parse('{{hello}}', 'hello'), None)

    def test_nothing(self):
        'do no actual parsing'
        r = parse('{{hello}}', '{hello}')
        self.assertEqual(r.fixed, ())
        self.assertEqual(r.named, {})

    def test_fixed(self):
        'pull a fixed value out of string'
        r = parse('hello {}', 'hello world')
        self.assertEqual(r.fixed, ('world', ))

    def test_left(self):
        'pull left-aligned text out of string'
        r = parse('{:<} world', 'hello       world')
        self.assertEqual(r.fixed, ('hello', ))

    def test_right(self):
        'pull right-aligned text out of string'
        r = parse('hello {:>}', 'hello       world')
        self.assertEqual(r.fixed, ('world', ))

    def test_center(self):
        'pull right-aligned text out of string'
        r = parse('hello {:^} world', 'hello  there     world')
        self.assertEqual(r.fixed, ('there', ))

    def test_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {:d} {:w}', 'hello 12 people')
        self.assertEqual(r.fixed, (12, 'people'))
        r = parse('hello {:w} {:w}', 'hello 12 people')
        self.assertEqual(r.fixed, ('12', 'people'))

    def test_typed_fail(self):
        'pull a named, typed values out of string'
        self.assertEqual(parse('hello {:d} {:w}', 'hello people 12'), None)

    def test_named(self):
        'pull a named value out of string'
        r = parse('hello {name}', 'hello world')
        self.assertEqual(r.named, {'name': 'world'})

    def test_mixed(self):
        'pull a fixed and named values out of string'
        r = parse('hello {} {name} {} {spam}', 'hello world and other beings')
        self.assertEqual(r.fixed, ('world', 'other'))
        self.assertEqual(r.named, dict(name='and', spam='beings'))

    def test_named_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {number:d} {things}', 'hello 12 people')
        self.assertEqual(r.named, dict(number=12, things='people'))
        r = parse('hello {number:w} {things}', 'hello 12 people')
        self.assertEqual(r.named, dict(number='12', things='people'))

    def test_named_aligned_typed(self):
        'pull a named, typed values out of string'
        r = parse('hello {number:<d} {things}', 'hello 12      people')
        self.assertEqual(r.named, dict(number=12, things='people'))
        r = parse('hello {number:>d} {things}', 'hello      12 people')
        self.assertEqual(r.named, dict(number=12, things='people'))
        r = parse('hello {number:^d} {things}', 'hello      12      people')
        self.assertEqual(r.named, dict(number=12, things='people'))

    def test_spans(self):
        'test the string sections our fields come from'
        string = 'hello world'
        r = parse('hello {}', string)
        self.assertEqual(r.spans, {0: (6,11)})
        start, end = r.spans[0]
        self.assertEqual(string[start:end], r.fixed[0])

        string = 'hello     world'
        r = parse('hello {:>}', string)
        self.assertEqual(r.spans, {0: (10,15)})
        start, end = r.spans[0]
        self.assertEqual(string[start:end], r.fixed[0])

        string = 'hello 0x12 world'
        r = parse('hello {val:x} world', string)
        self.assertEqual(r.spans, {'val': (6,10)})
        start, end = r.spans['val']
        self.assertEqual(string[start:end], '0x%x' % r.named['val'])

        string = 'hello world and other beings'
        r = parse('hello {} {name} {} {spam}', string)
        self.assertEqual(r.spans, {0: (6, 11), 'name': (12, 15),
            1: (16, 21), 'spam': (22, 28)})

    def test_numbers(self):
        'pull a numbers out of a string'
        def y(fmt, s, e, str_equals=False):
            p = compile(fmt)
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
            if parse(fmt, s) is not None:
                self.fail('%r matched %r' % (fmt, s))
        y('a {:d} b', 'a 12 b', 12)
        y('a {:5d} b', 'a    12 b', 12)
        y('a {:5d} b', 'a   -12 b', -12)
        y('a {:d} b', 'a -12 b', -12)
        n('a {:d} b', 'a +12 b', None)
        y('a {:-d} b', 'a -12 b', -12)
        n('a {:-d} b', 'a +12 b', None)
        y('a {:+d} b', 'a -12 b', -12)
        y('a {:+d} b', 'a +12 b', 12)
        y('a {: d} b', 'a -12 b', -12)
        y('a {: d} b', 'a  12 b', 12)
        n('a {: d} b', 'a +12 b', None)

        y('a {:n} b', 'a 100 b', 100)
        y('a {:n} b', 'a 1,000 b', 1000)
        y('a {:n} b', 'a 1.000 b', 1000)
        y('a {:n} b', 'a -1,000 b', -1000)
        y('a {:+n} b', 'a +1,000 b', 1000)
        y('a {:n} b', 'a 10,000 b', 10000)
        y('a {:n} b', 'a 100,000 b', 100000)
        n('a {:n} b', 'a 100,00 b', None)

        y('a {:f} b', 'a 12.0 b', 12.0)
        y('a {:f} b', 'a -12.1 b', -12.1)
        y('a {:-f} b', 'a -12.1 b', -12.1)
        y('a {:+f} b', 'a +12.1 b', 12.1)
        y('a {: f} b', 'a  12.1 b', 12.1)
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
        y('a {:+05d} b', 'a +00001 b', 1)

        y('a {:=d} b', 'a 000012 b', 12)
        y('a {:x=5d} b', 'a xxx12 b', 12)
        y('a {:x=5d} b', 'a -xxx12 b', -12)

    def test_datetimes(self):
        def y(fmt, s, e, tz=None):
            p = compile(fmt)
            r = p.parse(s)
            if r is None:
                self.fail('%r (%r) did not match %r' % (fmt, p._expression, s))
            r = r.fixed[0]
            self.assertEqual(r, e,
                '%r found %r in %r, not %r' % (fmt, r, s, e))
            if tz is not None:
                self.assertEqual(r.tzinfo, tz,
                    '%r found TZ %r in %r, not %r' % (fmt, r.tzinfo, s, e))
        def n(fmt, s, e):
            if parse(fmt, s) is not None:
                self.fail('%r matched %r' % (fmt, s))

        utc = FixedTzOffset(0, 'UTC')
        aest = FixedTzOffset(10*60, '+1000')

        # ISO 8660 variants
        # YYYY-MM-DD (eg 1997-07-16)
        y('a {:ti} b', 'a 1997-07-16 b', datetime(1997, 7, 16))

        # YYYY-MM-DDThh:mmTZD (eg 1997-07-16T19:20+01:00)
        y('a {:ti} b', 'a 1997-07-16T19:20 b', datetime(1997, 7, 16, 19, 20, 0))
        y('a {:ti} b', 'a 1997-07-16T19:20Z b',
            datetime(1997, 7, 16, 19, 20, tzinfo=utc))
        y('a {:ti} b', 'a 1997-07-16T19:20+01:00 b',
            datetime(1997, 7, 16, 19, 20, tzinfo=FixedTzOffset(60, '+01:00')))

        # YYYY-MM-DDThh:mm:ssTZD (eg 1997-07-16T19:20:30+01:00)
        y('a {:ti} b', 'a 1997-07-16T19:20:30 b', datetime(1997, 7, 16, 19, 20, 30))
        y('a {:ti} b', 'a 1997-07-16T19:20:30Z b',
            datetime(1997, 7, 16, 19, 20, 30, tzinfo=utc))
        y('a {:ti} b', 'a 1997-07-16T19:20:30+01:00 b',
            datetime(1997, 7, 16, 19, 20, 30, tzinfo= FixedTzOffset(60, '+01:00')))

        # YYYY-MM-DDThh:mm:ss.sTZD (eg 1997-07-16T19:20:30.45+01:00)
        y('a {:ti} b', 'a 1997-07-16T19:20:30.500000 b', datetime(1997, 7, 16, 19, 20, 30, 500000))
        y('a {:ti} b', 'a 1997-07-16T19:20:30.5Z b',
            datetime(1997, 7, 16, 19, 20, 30, 500000, tzinfo=utc))
        y('a {:ti} b', 'a 1997-07-16T19:20:30.5+01:00 b',
            datetime(1997, 7, 16, 19, 20, 30, 500000, tzinfo=FixedTzOffset(60, '+01:00')))

        aest_d = datetime(2011, 11, 21, 10, 21, 36, tzinfo=aest)
        dt = datetime(2011, 11, 21, 10, 21, 36)
        dt00 = datetime(2011, 11, 21, 10, 21)
        d = datetime(2011, 11, 21)

        # te   RFC2822 e-mail format        datetime
        y('a {:te} b', 'a Mon, 21 Nov 2011 10:21:36 +1000 b', aest_d)
        y('a {:te} b', 'a 21 Nov 2011 10:21:36 +1000 b', aest_d)

        # tg   global (day/month) format datetime
        y('a {:tg} b', 'a 21/11/2011 10:21:36 AM +1000 b', aest_d)
        y('a {:tg} b', 'a 21-11-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:tg} b', 'a 21/11/2011 10:21:36 +1000 b', aest_d)
        y('a {:tg} b', 'a 21/11/2011 10:21:36 b', dt)
        y('a {:tg} b', 'a 21/11/2011 10:21 b', dt00)
        y('a {:tg} b', 'a 21-11-2011 b', d)
        y('a {:tg} b', 'a 21-Nov-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:tg} b', 'a 21-November-2011 10:21:36 AM +1000 b', aest_d)

        # ta   US (month/day) format     datetime
        y('a {:ta} b', 'a 11/21/2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a 11-21-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a 11/21/2011 10:21:36 +1000 b', aest_d)
        y('a {:ta} b', 'a 11/21/2011 10:21:36 b', dt)
        y('a {:ta} b', 'a 11/21/2011 10:21 b', dt00)
        y('a {:ta} b', 'a 11-21-2011 b', d)
        y('a {:ta} b', 'a Nov-21-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a November-21-2011 10:21:36 AM +1000 b', aest_d)
        y('a {:ta} b', 'a November-21-2011 b', d)

        # th   HTTP log format date/time                   datetime
        y('a {:th} b', 'a 21/Nov/2011:10:21:36 +1000 b', aest_d)

        d = datetime(2011, 11, 21, 10, 21, 36)

        # tc   ctime() format           datetime
        y('a {:tc} b', 'a Mon Nov 21 10:21:36 2011 b', d)

        # tt   Time                                        time
        y('a {:tt} b', 'a 10:21:36 AM +1000 b', time(10, 21, 36, tzinfo=aest))


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
