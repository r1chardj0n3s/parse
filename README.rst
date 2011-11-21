Parse strings using a specification based on the Python format() syntax.

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
