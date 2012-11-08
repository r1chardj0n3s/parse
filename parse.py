r'''Parse strings using a specification based on the Python format() syntax.

   ``parse()`` is the opposite of ``format()``

The module is set up to only export ``parse()``, ``search()`` and
``findall()`` when ``import *`` is used:

>>> from parse import *

From there it's a simple thing to parse a string:

>>> parse("It's {}, I love it!", "It's spam, I love it!")
<Result ('spam',) {}>
>>> _[0]
'spam'

Or to search a string for some pattern:

>>> search('Age: {:d}\n', 'Name: Rufus\nAge: 42\nColor: red\n')
<Result (42,) {}>

Or find all the occurrances of some pattern in a string:

>>> ''.join(r.fixed[0] for r in findall(">{}<", "<p>some <b>bold</b> text</p>"))
'some bold text'

If you're going to use the same pattern to match lots of strings you can
compile it once:

>>> from parse import compile
>>> p = compile("It's {}, I love it!")
>>> print p
<Parser "It's {}, I love it!">
>>> p.parse("It's spam, I love it!")
<Result ('spam',) {}>

("compile" is not exported for ``import *`` usage as it would override the
built-in ``compile()`` function)


Format Syntax
-------------

A basic version of the `Format String Syntax`_ is supported with anonymous
(fixed-position), named and formatted fields::

   {[field name]:[format spec]}

Field names must be a valid Python identifiers, including dotted names;
element indexes are supported (as they would make no sense.)

Numbered fields are also not supported: the result of parsing will include
the parsed fields in the order they are parsed.

The conversion of fields to types other than strings is done based on the
type in the format specification, which mirrors the ``format()`` behaviour.
There are no "!" field conversions like ``format()`` has.

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
>>> print r['item']
hand grenade

Dotted names are possible though the application must make additional sense of
the result:

>>> r = parse("Mmm, {food.type}, I love it!", "Mmm, spam, I love it!")
>>> print r
<Result () {'food.type': 'spam'}>
>>> print r.named
{'food.type': 'spam'}
>>> print r['food.type']
spam


Format Specification
--------------------

Do remember that most often a straight format-less "{}" will suffice
where a more complex format specification might have been used.

Most of the `Format Specification Mini-Language`_ is supported::

   [[fill]align][0][width][type]

The align operators will cause spaces (or specified fill character)
to be stripped from the value. Similarly width is not enforced; it
just indicates there may be whitespace or "0"s to strip.

The "#" format character is handled automatically by d, b, o and x -
that is: if there is a "0b", "0o" or "0x" prefix respectively, it's
handled. For "d" any will be accepted, but for the others the correct
prefix must be present if at all. Similarly number sign is handled
automatically.

The types supported are a slightly different mix to the format() types.  Some
format() types come directly over: "d", "n", "%", "f", "e", "b", "o" and "x".
In addition some regular expression character group types "D", "w", "W", "s" and
"S" are also available.

The "e" and "g" types are case-insensitive so there is not need for
the "E" or "G" types.

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
 %    Percentage (converted to value/100.0)       float
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

Some examples of typed parsing with ``None`` returned if the typing
does not match:

>>> parse('Our {:d} {:w} are...', 'Our 3 weapons are...')
<Result (3, 'weapons') {}>
>>> parse('Our {:d} {:w} are...', 'Our three weapons are...')
>>> parse('Meet at {:tg}', 'Meet at 1/2/2011 11:00 PM')
<Result (datetime.datetime(2011, 2, 1, 23, 0),) {}>

And messing about with alignment:

>>> parse('with {:>} herring', 'with     a herring')
<Result ('a',) {}>
>>> parse('spam {:^} spam', 'spam    lovely     spam')
<Result ('lovely',) {}>

Note that the "center" alignment does not test to make sure the value is
centered - it just strips leading and trailing whitespace.

Some notes for the date and time types:

- the presence of the time part is optional (including ISO 8601, starting
  at the "T"). A full datetime object will always be returned; the time
  will be set to 00:00:00. You may also specify a time without seconds.
- when a seconds amount is present in the input fractions will be parsed
  to give microseconds.
- except in ISO 8601 the day and month digits may be 0-padded.
- the date separator for the tg and ta formats may be "-" or "/".
- named months (abbreviations or full names) may be used in the ta and tg
  formats in place of numeric months.
- as per RFC 2822 the e-mail format may omit the day (and comma), and the
  seconds but nothing else.
- hours greater than 12 will be happily accepted.
- the AM/PM are optional, and if PM is found then 12 hours will be added
  to the datetime object's hours amount - even if the hour is greater
  than 12 (for consistency.)
- except in ISO 8601 and e-mail format the timezone is optional.
- named timezones are not handled yet.

Note: attempting to match too many datetime fields in a single parse() will
currently result in a resource allocation issue. A TooManyFields exception
will be raised in this instance. The current limit is about 15. It is hoped
that this limit will be removed one day.

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


Custom Type Conversions
-----------------------

If you wish to have matched fields automatically converted to your own type you
may pass in a dictionary of type conversion information to ``parse()`` and
``compile()``.

The converter will be passed the field string matched. Whatever it returns
will be substituted in the ``Result`` instance for that field.

Your custom type conversions may override the builtin types if you supply one
with the same identifier.

>>> def shouty(string):
...    return string.upper()
...
>>> parse('{:shouty} world', 'hello world', dict(shouty=shouty))
<Result ('HELLO',) {}>


If the type-converter has the optional ``pattern`` attribute, it is used as
regular expression for better pattern matching (instead of the default one).
You can also use the ``with_pattern(pattern)`` decorator to add this
information to a type-converter function:

>>> import parse
>>> @parse.with_pattern(r'\d+')
... def parse_number(text):
...    return int(text)
>>> assert parse_number.pattern == r'\d+'
>>> schema = 'Answer: {number:Number}'
>>> parse.parse(schema, 'Answer: 42', dict(Number=parse_number))
<Result () {'number': 42}>
>>> _ = parse.parse(schema, 'Answer: Alice', dict(Number=parse_number))
>>> assert _ is None, "EXPECT MISMATCH"

----

**Unreleased Changes**:

- Add optional cardinality field support after type field in parse expressions.
- Add Cardinality, TypeBuilder classes to support different cardinality.
- Add parse_type module to simplify type creation for common use cases.
- Add with_pattern() decorator for type-converter functions.
- Add support for optional 'pattern' attribute in user-defined types.

**Version history (in brief)**:

- 1.5.3 fix handling of question marks
- 1.5.2 fix type conversion error with dotted names (thanks Sebastian Thiel)
- 1.5.1 implement handling of named datetime fields
- 1.5 add handling of dotted field names (thanks Sebastian Thiel)
- 1.4.1 fix parsing of "0" in int conversion (thanks James Rowe)
- 1.4 add __getitem__ convenience access on Result.
- 1.3.3 fix Python 2.5 setup.py issue.
- 1.3.2 fix Python 3.2 setup.py issue.
- 1.3.1 fix a couple of Python 3.2 compatibility issues.
- 1.3 added search() and findall(); removed compile() from ``import *``
  export as it overwrites builtin.
- 1.2 added ability for custom and override type conversions to be
  provided; some cleanup
- 1.1.9 to keep things simpler number sign is handled automatically;
  significant robustification in the face of edge-case input.
- 1.1.8 allow "d" fields to have number base "0x" etc. prefixes;
  fix up some field type interactions after stress-testing the parser;
  implement "%" type.
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

This code is copyright 2012 Richard Jones <richard@python.org>
See the end of the source file for the license of use.
'''
__version__ = '1.5.3.4'

# yes, I now have two problems
import re
import sys
from datetime import datetime, time, tzinfo, timedelta
from functools import partial
import logging

__all__ = 'parse search findall'.split()

log = logging.getLogger(__name__)


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

        if string[0] == '0' and len(string) > 1:
            if string[1] in 'bB':
                base = 2
            elif string[1] in 'oO':
                base = 8
            elif string[1] in 'xX':
                base = 16
            else:
                # just go with the base specifed
                pass

        chars = CHARS[:base]
        string = re.sub('[^%s]' % chars, '', string.lower())
        return sign * int(string, base)
    return f


def percentage(string, match):
    return float(string[:-1]) / 100.


class FixedTzOffset(tzinfo):
    """Fixed offset in minutes east from UTC.
    """
    ZERO = timedelta(0)

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
        return self.ZERO

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
TIME_PAT = r'(\d{1,2}:\d{1,2}(:\d{1,2}(\.\d+)?)?)'
AM_PAT = r'(\s+[AP]M)'
TZ_PAT = r'(\s+[-+]\d\d?:?\d\d)'

def date_convert(string, match, ymd=None, mdy=None, dmy=None,
        d_m_y=None, hms=None, am=None, tz=None):
    '''Convert the incoming string containing some date / time info into a
    datetime instance.
    '''
    groups = match.groups()
    time_only = False
    if ymd is not None:
        y, m, d = re.split('[-/\s]', groups[ymd])
    elif mdy is not None:
        m, d, y = re.split('[-/\s]', groups[mdy])
    elif dmy is not None:
        d, m, y = re.split('[-/\s]', groups[dmy])
    elif d_m_y is not None:
        d, m, y = d_m_y
        d = groups[d]
        m = groups[m]
        y = groups[y]
    else:
        time_only = True

    H = M = S = u = 0
    if hms is not None and groups[hms]:
        t = groups[hms].split(':')
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

    if am is not None:
        am = groups[am]
        if am and am.strip() == 'PM':
            H += 12

    if tz is not None:
        tz = groups[tz]
    if tz == 'Z':
        tz = FixedTzOffset(0, 'UTC')
    elif tz:
        tz = tz.strip()
        if tz.isupper():
            # TODO use the awesome python TZ module?
            pass
        else:
            sign = tz[0]
            if ':' in tz:
                tzh, tzm = tz[1:].split(':')
            else:
                tzh, tzm = tz[1:3], tz[3:5]
            offset = int(tzm) + int(tzh) * 60
            if sign == '-':
                offset = -offset
            tz = FixedTzOffset(offset, tz)

    if time_only:
        d = time(H, M, S, u, tzinfo=tz)
    else:
        y = int(y)
        if m.isdigit():
            m = int(m)
        else:
            m = MONTHS_MAP[m]
        d = int(d)
        d = datetime(y, m, d, H, M, S, u, tzinfo=tz)

    return d


class TooManyFields(ValueError):
    pass

# note: {} are handled separately
REGEX_SAFETY = re.compile(r'([?\\.[\]()*+\^$!])')

# allowed field types
ALLOWED_TYPES = set(list('nbox%fegwWdDsS') +
   ['t'+c for c in 'ieahgct'])

# -----------------------------------------------------------------------------
# CLASS: Cardinality (Field Part)
# -----------------------------------------------------------------------------
class Cardinality(object):
    """
    Cardinality field for parse format expression, ala:

        "... {person:Person?} ..."   -- OPTIONAL: Cardinality zero or one, 0..1
        "... {persons:Person*} ..."  -- MANY0: Cardinality zero or more, 0..
        "... {persons:Person+} ..."  -- MANY:  Cardinality one  or more, 1..
    """
    one = 1
    zero_or_one  = 2
    zero_or_more = 3
    one_or_more  = 4

    # -- ALIASES:
    optional = zero_or_one
    many = one_or_more

    # -- MAPPING SUPPORT:
    pattern_chars = "?*+"
    from_char_map = {
        '?': zero_or_one,
        '*': zero_or_more,
        '+': one_or_more,
    }

    @classmethod
    def make_zero_or_one_pattern(cls, pattern):
        return r"(%s)?" % pattern

    @classmethod
    def make_zero_or_more_pattern(cls, pattern, listsep=','):
        return r"(%s)?(\s*%s\s*(%s))*" % (pattern, listsep, pattern)

    @classmethod
    def make_one_or_more_pattern(cls, pattern, listsep=','):
        return r"(%s)(\s*%s\s*(%s))*" % (pattern, listsep, pattern)

# -- OPTIONAL CODE:
#    @classmethod
#    def make_pattern_for(cls, cardinality, pattern, listsep=','):
#        """
#        Creates a new regular expression pattern for the cardinality.
#
#        :param cardinality: Cardinality case (zero_or_one, zero_or_more, ...)
#        :param pattern:  Regex pattern for cardinality one (as text).
#        :param listsep:  Optional list separator for many (default: comma ',').
#        :return: New regular expression pattern for this cardinality case.
#        """
#        if cardinality == cls.zero_or_one:
#            return cls.make_zero_or_one_pattern(pattern)
#        elif cardinality == cls.zero_or_more:
#            return cls.make_zero_or_more_pattern(pattern, listsep)
#        elif cardinality == cls.one_or_more:
#            return cls.make_one_or_more_pattern(pattern, listsep)
#            # -- OTHERWISE, EXPECT: Cardinality one, otherwise OOPS.
#        assert cls.is_one(cardinality), "Unknown value: %s" % cardinality
#        return pattern
#
#    @classmethod
#    def is_one(cls, cardinality):
#        return cardinality == cls.one or cardinality is None
#
#    @classmethod
#    def is_many(cls, cardinality):
#        return cardinality == cls.one_or_more or cardinality == cls.zero_or_more
#
# -----------------------------------------------------------------------------
# CLASS: TypeBuilder
# -----------------------------------------------------------------------------
class TypeBuilder(object):
    """
    Provides a utility class to build type-converters (parse_types) for parse.
    It supports to build new type-converters for different cardinality
    based on the type-converter for cardinality one.
    """
    default_pattern = r".+?"

    @classmethod
    def with_zero_or_one(cls, parse_type):
        """
        Creates a type-converter function for a T with 0..1 times
        by using the type-converter for one item of T.

        :param parse_type: Type-converter (function) for data type T.
        :return: type-converter for optional<T> (T or None).
        """
        def parse_optional(text, m=None):
            if text:
                text = text.strip()
            if not text:
                return None
            return parse_type(text)
        pattern = getattr(parse_type, "pattern", cls.default_pattern)
        new_pattern = Cardinality.make_zero_or_one_pattern(pattern)
        parse_optional.pattern = new_pattern
        return parse_optional

    @classmethod
    def with_zero_or_more(cls, parse_type, listsep=",", max_size=None):
        """
        Creates a type-converter function for a list<T> with 0..N items
        by using the type-converter for one item of T.

        :param parse_type: Type-converter (function) for data type T.
        :param listsep:  Optional list separator between items (default: ',')
        :param max_size: Optional max. number of items constraint (future).
        :return: type-converter for list<T>
        """
        def parse_list0(text, m=None):
            if text:
                text = text.strip()
            if not text:
                return []
            parts = [ parse_type(texti.strip())
                      for texti in text.split(listsep) ]
            return parts
        pattern  = getattr(parse_type, "pattern", cls.default_pattern)
        list_pattern = Cardinality.make_zero_or_more_pattern(pattern, listsep)
        parse_list0.pattern  = list_pattern
        parse_list0.max_size = max_size
        return parse_list0

    @classmethod
    def with_one_or_more(cls, parse_type, listsep=",", max_size=None):
        """
        Creates a type-converter function for a list<T> with 1..N items
        by using the type-converter for one item of T.

        :param parse_type: Type-converter (function) for data type T.
        :param listsep:  Optional list separator between items (default: ',')
        :param max_size: Optional max. number of items constraint (future).
        :return: type-converter for list<T>
        """
        def parse_list(text, m=None):
            parts = [ parse_type(texti.strip())
                      for texti in text.split(listsep) ]
            return parts
        pattern = getattr(parse_type, "pattern", cls.default_pattern)
        list_pattern = Cardinality.make_one_or_more_pattern(pattern, listsep)
        parse_list.pattern  = list_pattern
        parse_list.max_size = max_size
        return parse_list

    # -- ALIAS METHODS:
    @classmethod
    def with_optional(cls, parse_type):
        """Alias for :py:meth:`with_zero_or_one` method."""
        return cls.with_zero_or_one(parse_type)

    @classmethod
    def with_many(cls, parse_type, **kwargs):
        """Alias for :py:meth:`with_one_or_more` method."""
        return cls.with_one_or_more(parse_type, **kwargs)

    @classmethod
    def with_many0(cls, parse_type, **kwargs):
        """Alias for :py:meth:`with_zero_or_more` method."""
        return cls.with_zero_or_more(parse_type, **kwargs)

# -----------------------------------------------------------------------------
# DECORATOR: with_pattern
# -----------------------------------------------------------------------------
def with_pattern(pattern):
    """
    Provides a decorator for type-converter (parse_type) functions.
    Annotates the type converter with the :attr:`pattern` attribute.

    EXAMPLE:
        >>> import parse
        >>> @parse.with_pattern(r"\d+")
        ... def parse_number(text):
        ...     return int(text)

    is equivalent to:

        >>> def parse_number(text):
        ...     return int(text)
        >>> parse_number.pattern = r"\d+"

    :param pattern:  Regular expression pattern (as text).
    :return: Wrapped function
    """
    def decorator(func):
        func.pattern = pattern
        return func
    return decorator

# -----------------------------------------------------------------------------
# FUNCTIONS: Parse Helpers
# -----------------------------------------------------------------------------
def extract_format(format, extra_types):
    '''Pull apart the format [[fill]align][0][width][type]
    '''
    fill = align = None
    if format[0] in '<>=^':
        align = format[0]
        format = format[1:]
    elif len(format) > 1 and format[1] in '<>=^':
        fill = format[0]
        align = format[1]
        format = format[2:]

    zero = False
    if format and format[0] == '0':
        zero = True
        format = format[1:]

    width = ''
    while format:
        if not format[0].isdigit():
            break
        width += format[0]
        format = format[1:]
    # -- CARDINALITY-FIELD:
    cardinality = None
    if format and format[-1] in Cardinality.pattern_chars:
        _cardinality_char = format[-1]
        cardinality = Cardinality.from_char_map[_cardinality_char]
        format = format[:-1]
        assert format, "Type information is required for cardinality"
    # -- CARDINALITY-FIELD END.

    # the rest is the type, if present
    type = format
    if type and type not in ALLOWED_TYPES and type not in extra_types:
        raise ValueError('type %r not recognised' % type)

    return locals()


PARSE_RE = re.compile(r'({{|}}|{}|{:[^}]+?}|{\w+?(?:\.\w+?)*}|{\w+?(?:\.\w+?)*:[^}]+?})')


class Parser(object):
    '''Encapsulate a format string that may be used to parse other strings.
    '''
    def __init__(self, format, extra_types={}):
        # a mapping of a name as in {hello.world} to a regex-group compatible name, like hello__world
        # Its used to prevent the transformation of name-to-group and group to name to fail subtly, such
        # as in: hello_.world-> hello___world->hello._world
        self._group_to_name_map = {}
        self._format = format
        self._extra_types = extra_types
        self._fixed_fields = []
        self._named_fields = []
        self._group_index = 0
        self._type_conversions = {}
        self._expression = self._generate_expression()
        self.__search_re = None
        self.__match_re = None

        logging.debug('format %r -> %r' % (format, self._expression))

    def __repr__(self):
        if len(self._format) > 20:
            return '<%s %r>' % (self.__class__.__name__, self._format[:17] + '...')
        return '<%s %r>' % (self.__class__.__name__, self._format)

    @property
    def _search_re(self):
        if self.__search_re is None:
            try:
                self.__search_re = re.compile(self._expression, re.IGNORECASE|re.DOTALL)
            except AssertionError:
                e = sys.exc_info()[1]   # to keep py3k and backward compat
                if str(e).endswith('this version only supports 100 named groups'):
                    raise TooManyFields('sorry, you are attempting to parse too '
                        'many complex fields')
        return self.__search_re

    @property
    def _match_re(self):
        if self.__match_re is None:
            expression = '^%s$' % self._expression
            try:
                self.__match_re = re.compile(expression, re.IGNORECASE|re.DOTALL)
            except AssertionError:
                e = sys.exc_info()[1]   # to keep py3k and backward compat
                if str(e).endswith('this version only supports 100 named groups'):
                    raise TooManyFields('sorry, you are attempting to parse too '
                        'many complex fields')
            except re.error:
                raise NotImplementedError("Group names (e.g. (?P<name>) can cause failure, as they are not esacped properly: '%s'" % expression)
        return self.__match_re

    def parse(self, string):
        '''Match my format to the string exactly.

        Return either a Result instance or None if there's no match.
        '''
        m = self._match_re.match(string)
        if m is None:
            return None

        return self._generate_result(m)

    def search(self, string, pos=0, endpos=None):
        '''Search the string for my format.

        Optionally start the search at "pos" character index and limit the
        search to a maximum index of endpos - equivalent to
        search(string[:endpos]).

        Return either a Result instance or None if there's no match.
        '''
        if endpos is None:
            endpos = len(string)
        m = self._search_re.search(string, pos, endpos)
        if m is None:
            return None

        return self._generate_result(m)

    def findall(self, string, pos=0, endpos=None, extra_types={}):
        '''Search "string" for the all occurrances of "format".

        Optionally start the search at "pos" character index and limit the
        search to a maximum index of endpos - equivalent to
        search(string[:endpos]).

        Returns an iterator that holds Result instances for each format match
        found.
        '''
        if endpos is None:
            endpos = len(string)
        return ResultIterator(self, string, pos, endpos)

    def _generate_result(self, m):
        # ok, figure the fixed fields we've pulled out and type convert them
        fixed_fields = list(m.groups())
        for n in self._fixed_fields:
            if n in self._type_conversions:
                fixed_fields[n] = self._type_conversions[n](fixed_fields[n], m)
        fixed_fields = tuple(fixed_fields[n] for n in self._fixed_fields)

        # grab the named fields, converting where requested
        groupdict = m.groupdict()
        named_fields = {}
        name_map = {}
        for k in self._named_fields:
            korig = self._group_to_name_map[k]
            name_map[korig] = k
            if k in self._type_conversions:
                named_fields[korig] = self._type_conversions[k](groupdict[k], m)
            else:
                named_fields[korig] = groupdict[k]

        # now figure the match spans
        spans = dict((n, m.span(name_map[n])) for n in named_fields)
        spans.update((i, m.span(n+1)) for i, n in enumerate(self._fixed_fields))

        # and that's our result
        return Result(fixed_fields, named_fields, spans)

    def _regex_replace(self, match):
        return '\\' + match.group(1)

    def _generate_expression(self):
        # turn my _format attribute into the _expression attribute
        e = []
        for part in PARSE_RE.split(self._format):
            if not part:
                continue
            elif part == '{{':
                e.append(r'\{')
            elif part == '}}':
                e.append(r'\}')
            elif part[0] == '{':
                # this will be a braces-delimited field to handle
                e.append(self._handle_field(part))
            else:
                # just some text to match
                e.append(REGEX_SAFETY.sub(self._regex_replace, part))
        return ''.join(e)

    def _to_group_name(self, field):
        # return a version of field which can be used as capture group, even
        # though it might contain '.'
        group = field.replace('.', '_')

        # make sure we don't collide
        n = 1
        while group in self._group_to_name_map:
            n += 1
            if '.' in field:
                group = field.replace('.', '_'*n)
            else:
                group = field.replace('_', '_'*n)

        # save off the mapping
        self._group_to_name_map[group] = field
        return group

    def _handle_field(self, field):
        # first: lose the braces
        field = field[1:-1]

        # now figure whether this is an anonymous or named field, and whether
        # there's any format specification
        format = ''
        if field and field[0].isalpha():
            if ':' in field:
                name, format = field.split(':')
            else:
                name = field
            group = self._to_group_name(name)
            self._named_fields.append(group)
            # this will become a group, which must not contain dots
            wrap = '(?P<%s>%%s)' % group
        else:
            self._fixed_fields.append(self._group_index)
            wrap = '(%s)'
            if ':' in field:
                format = field[1:]
            group = self._group_index

        # simplest case: no type specifier ({} or {name})
        if not format:
            self._group_index += 1
            return wrap % '.+?'

        # decode the format specification
        format = extract_format(format, self._extra_types)
        cardinality = format["cardinality"]

        # figure type conversions, if any
        type = format['type']
        is_numeric = type and type in 'n%fegdobh'
        if type in self._extra_types:
            type_converter = self._extra_types[type]
            s = getattr(type_converter, 'pattern', TypeBuilder.default_pattern)
            if cardinality == Cardinality.one_or_more:
                # -- CASE MANY one_or_more: list<T> as comma-separated list.
                f = TypeBuilder.with_one_or_more(type_converter)
                s = f.pattern
            elif cardinality == Cardinality.zero_or_more:
                # -- CASE MANY zero_or_more: list<T> as comma-separated list.
                f = TypeBuilder.with_zero_or_more(type_converter)
                s = f.pattern
            elif cardinality == Cardinality.zero_or_one:
                # -- CASE zero_or_one: optional<T> := T or None
                f = TypeBuilder.with_zero_or_one(type_converter)
                # -- NOT HERE: s = f.pattern
                #    OPTIONAL case is better handled below.
            else:
                # -- CASE one: T
                def f(string, m):
                    return type_converter(string)
            self._type_conversions[group] = f
        elif type == 'n':
            s = '\d{1,3}([,.]\d{3})*'
            self._group_index += 1
            self._type_conversions[group] = int_convert(10)
        elif type == 'b':
            s = '(0[bB])?[01]+'
            self._type_conversions[group] = int_convert(2)
            self._group_index += 1
        elif type == 'o':
            s = '(0[oO])?[0-7]+'
            self._type_conversions[group] = int_convert(8)
            self._group_index += 1
        elif type == 'x':
            s = '(0[xX])?[0-9a-fA-F]+'
            self._type_conversions[group] = int_convert(16)
            self._group_index += 1
        elif type == '%':
            s = r'\d+(\.\d+)?%'
            self._group_index += 1
            self._type_conversions[group] = percentage
        elif type == 'f':
            s = r'\d+\.\d+'
            self._type_conversions[group] = lambda s, m: float(s)
        elif type == 'e':
            s = r'\d+\.\d+[eE][-+]?\d+|nan|NAN|[-+]?inf|[-+]?INF'
            self._type_conversions[group] = lambda s, m: float(s)
        elif type == 'g':
            s = r'\d+(\.\d+)?([eE][-+]?\d+)?|nan|NAN|[-+]?inf|[-+]?INF'
            self._group_index += 2
            self._type_conversions[group] = lambda s, m: float(s)
        elif type == 'd':
            s = r'\d+|0[xX][0-9a-fA-F]+|[0-9a-fA-F]+|0[bB][01]+|0[oO][0-7]+'
            self._type_conversions[group] = int_convert(10)
        elif type == 'ti':
            s = r'(\d{4}-\d\d-\d\d)((\s+|T)%s)?(Z|[-+]\d\d:\d\d)?' % TIME_PAT
            n = self._group_index
            self._type_conversions[group] = partial(date_convert, ymd=n+1,
                hms=n+4, tz=n+7)
            self._group_index += 7
        elif type == 'tg':
            s = r'(\d{1,2}[-/](\d{1,2}|%s)[-/]\d{4})(\s+%s)?%s?%s?' % (
                ALL_MONTHS_PAT, TIME_PAT, AM_PAT, TZ_PAT)
            n = self._group_index
            self._type_conversions[group] = partial(date_convert, dmy=n+1,
                hms=n+5, am=n+8, tz=n+9)
            self._group_index += 9
        elif type == 'ta':
            s = r'((\d{1,2}|%s)[-/]\d{1,2}[-/]\d{4})(\s+%s)?%s?%s?' % (
                ALL_MONTHS_PAT, TIME_PAT, AM_PAT, TZ_PAT)
            n = self._group_index
            self._type_conversions[group] = partial(date_convert, mdy=n+1,
                hms=n+5, am=n+8, tz=n+9)
            self._group_index += 9
        elif type == 'te':
            # this will allow microseconds through if they're present, but meh
            s = r'(%s,\s+)?(\d{1,2}\s+%s\s+\d{4})\s+%s%s' % (DAYS_PAT,
                MONTHS_PAT, TIME_PAT, TZ_PAT)
            n = self._group_index
            self._type_conversions[group] = partial(date_convert, dmy=n+3,
                hms=n+5, tz=n+8)
            self._group_index += 8
        elif type == 'th':
            # slight flexibility here from the stock Apache format
            s = r'(\d{1,2}[-/]%s[-/]\d{4}):%s%s' % (MONTHS_PAT, TIME_PAT,
                TZ_PAT)
            n = self._group_index
            self._type_conversions[group] = partial(date_convert, dmy=n+1,
                hms=n+3, tz=n+6)
            self._group_index += 6
        elif type == 'tc':
            s = r'(%s)\s+%s\s+(\d{1,2})\s+%s\s+(\d{4})' % (
                DAYS_PAT, MONTHS_PAT, TIME_PAT)
            n = self._group_index
            self._type_conversions[group] = partial(date_convert,
                d_m_y=(n+4,n+3,n+8), hms=n+5)
            self._group_index += 8
        elif type == 'tt':
            s = r'%s?%s?%s?' % (TIME_PAT, AM_PAT, TZ_PAT)
            n = self._group_index
            self._type_conversions[group] = partial(date_convert, hms=n+1,
                am=n+4, tz=n+5)
            self._group_index += 5
        elif type:
            s = r'\%s+' % type
        else:
            s = '.+?'

        align = format['align']
        fill = format['fill']

        # handle some numeric-specific things like fill and sign
        if is_numeric:
            # prefix with something (align "=" trumps zero)
            if align == '=':
                # special case - align "=" acts like the zero above but with
                # configurable fill defaulting to "0"
                if not fill:
                    fill = '0'
                s = '%s*' % fill + s
            elif format['zero']:
                s = '0*' + s

            # allow numbers to be prefixed with a sign
            s = r'[-+ ]?' + s

        if not fill:
            fill = ' '

        if cardinality == Cardinality.zero_or_one:
            # -- CARDINALITY: Make field optional.
            assert wrap, "Cardinality requires wrap"
            wrap += '?'

        # Place into a group now - this captures the value we want to keep.
        # Everything else from now is just padding to be stripped off
        if wrap:
            s = wrap % s
            self._group_index += 1

        if format['width']:
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
    '''The result of a parse() or search().

    Fixed results may be looked up using result[index]. Named results may be
    looked up using result['name'].
    '''
    def __init__(self, fixed, named, spans):
        self.fixed = fixed
        self.named = named
        self.spans = spans

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.fixed[item]
        return self.named[item]

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.fixed,
            self.named)


class ResultIterator(object):
    '''The result of a findall() operation.

    Each element is a Result instance.
    '''
    def __init__(self, parser, string, pos, endpos):
        self.parser = parser
        self.string = string
        self.pos = pos
        self.endpos = endpos

    def __iter__(self):
        return self

    def __next__(self):
        m = self.parser._search_re.search(self.string, self.pos, self.endpos)
        if m is None:
            raise StopIteration()
        self.pos = m.end()
        return self.parser._generate_result(m)

    # pre-py3k compat
    next = __next__


def parse(format, string, extra_types={}):
    '''Using "format" attempt to pull values from "string".

    The format must match the string contents exactly. If the value
    you're looking for is instead just a part of the string use
    search().

    The return value will be an Result instance with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If the format is invalid a ValueError will be raised.

    See the module documentation for the use of "extra_types".

    In the case there is no match parse() will return None.
    '''
    return Parser(format, extra_types=extra_types).parse(string)


def search(format, string, pos=0, endpos=None, extra_types={}):
    '''Search "string" for the first occurance of "format".

    The format may occur anywhere within the string. If
    instead you wish for the format to exactly match the string
    use parse().

    Optionally start the search at "pos" character index and limit the search to
    a maximum index of endpos - equivalent to search(string[:endpos]).

    The return value will be an Result instance with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If the format is invalid a ValueError will be raised.

    See the module documentation for the use of "extra_types".

    In the case there is no match parse() will return None.
    '''
    return Parser(format, extra_types=extra_types).search(string, pos, endpos)


def findall(format, string, pos=0, endpos=None, extra_types={}):
    '''Search "string" for the all occurrances of "format".

    You will be returned an iterator that holds Result instances
    for each format match found.

    Optionally start the search at "pos" character index and limit the search to
    a maximum index of endpos - equivalent to search(string[:endpos]).

    Each Result instance has two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If the format is invalid a ValueError will be raised.

    See the module documentation for the use of "extra_types".
    '''
    return Parser(format, extra_types=extra_types).findall(string, pos, endpos)


def compile(format, extra_types={}):
    '''Create a Parser instance to parse "format".

    The resultant Parser has a method .parse(string) which
    behaves in the same manner as parse(format, string).

    Use this function if you intend to parse many strings
    with the same format.

    See the module documentation for the use of "extra_types".

    Returns a Parser instance.
    '''
    return Parser(format, extra_types=extra_types)


# Copyright (c) 2012 Richard Jones <richard@python.org>
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
