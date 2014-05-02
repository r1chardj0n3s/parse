Parse strings using a specification based on the Python format() syntax.

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

>>> ''.join(r.fixed[0] for r in findall(">{}<", "<p>the <b>bold</b> text</p>"))
'the bold text'

If you're going to use the same pattern to match lots of strings you can
compile it once:

>>> from parse import compile
>>> p = compile("It's {}, I love it!")
>>> print(p)
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
>>> print(r)
<Result ('knights', 'Ni!') {}>
>>> print(r.fixed)
('knights', 'Ni!')
>>> r = parse("Bring out the holy {item}", "Bring out the holy hand grenade")
>>> print(r)
<Result () {'item': 'hand grenade'}>
>>> print(r.named)
{'item': 'hand grenade'}
>>> print(r['item'])
hand grenade

Dotted names are possible though the application must make additional sense of
the result:

>>> r = parse("Mmm, {food.type}, I love it!", "Mmm, spam, I love it!")
>>> print(r)
<Result () {'food.type': 'spam'}>
>>> print(r.named)
{'food.type': 'spam'}
>>> print(r['food.type'])
spam


Format Specification
--------------------

Most often a straight format-less ``{}`` will suffice where a more complex
format specification might have been used.

Most of `format()`'s `Format Specification Mini-Language`_ is supported:

   [[fill]align][0][width][type]

The differences between `parse()` and `format()` are:

- The align operators will cause spaces (or specified fill character) to be
  stripped from the parsed value. The width is not enforced; it just indicates
  there may be whitespace or "0"s to strip.
- Numeric parsing will automatically handle a "0b", "0o" or "0x" prefix.
  That is, the "#" format character is handled automatically by d, b, o
  and x formats. For "d" any will be accepted, but for the others the correct
  prefix must be present if at all.
- Numeric sign is handled automatically.
- The thousands separator is handled automatically if the "n" type is used.
- The types supported are a slightly different mix to the format() types.  Some
  format() types come directly over: "d", "n", "%", "f", "e", "b", "o" and "x".
  In addition some regular expression character group types "D", "w", "W", "s"
  and "S" are also available.
- The "e" and "g" types are case-insensitive so there is not need for
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
      e.g. 1972-01-20T10:21:36Z ("T" and "Z"
      optional)
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
- in ISO 8601 the "Z" (UTC) timezone part may be a numeric offset
- timezones are specified as "+HH:MM" or "-HH:MM". The hour may be one or two
  digits (0-padded is OK.) Also, the ":" is optional.
- the timezone is optional in all except the e-mail format (it defaults to
  UTC.)
- named timezones are not handled yet.

Note: attempting to match too many datetime fields in a single parse() will
currently result in a resource allocation issue. A TooManyFields exception
will be raised in this instance. The current limit is about 15. It is hoped
that this limit will be removed one day.

.. _`Format String Syntax`:
  http://docs.python.org/library/string.html#format-string-syntax
.. _`Format Specification Mini-Language`:
  http://docs.python.org/library/string.html#format-specification-mini-language


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

If the type converter has the optional ``pattern`` attribute, it is used as
regular expression for better pattern matching (instead of the default one).

>>> def parse_number(text):
...    return int(text)
>>> parse_number.pattern = r'\d+'
>>> parse('Answer: {number:Number}', 'Answer: 42', dict(Number=parse_number))
<Result () {'number': 42}>
>>> _ = parse('Answer: {:Number}', 'Answer: Alice', dict(Number=parse_number))
>>> assert _ is None, "MISMATCH"

You can also use the ``with_pattern(pattern)`` decorator to add this
information to a type converter function:

>>> from parse import with_pattern
>>> @with_pattern(r'\d+')
... def parse_number(text):
...    return int(text)
>>> parse('Answer: {number:Number}', 'Answer: 42', dict(Number=parse_number))
<Result () {'number': 42}>

A more complete example of a custom type might be:

>>> yesno_mapping = {
...     "yes":  True,   "no":    False,
...     "on":   True,   "off":   False,
...     "true": True,   "false": False,
... }
... @with_pattern(r"|".join(yesno_mapping))
... def parse_yesno(text):
...     return yesno_mapping[text.lower()]


----

**Version history (in brief)**:

- 1.6.4 handle pipe "|" characters in parse string (thanks Martijn Pieters)
- 1.6.3 handle repeated instances of named fields, fix bug in PM time
  overflow
- 1.6.2 fix logging to use local, not root logger (thanks Necku)
- 1.6.1 be more flexible regarding matched ISO datetimes and timezones in
  general, fix bug in timezones without ":" and improve docs
- 1.6.0 add support for optional ``pattern`` attribute in user-defined types
  (thanks Jens Engel)
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

This code is copyright 2012-2013 Richard Jones <richard@python.org>
See the end of the source file for the license of use.
