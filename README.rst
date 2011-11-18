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

Most of the `Format Specification Mini-Language`_ is supported::

   [[fill]align][sign][#][0][width][,][.precision][type]

The align operators will cause spaces (or specified fill character)
to be stripped from the value. The alignment character "=" is not yet
supported.

The comma "," separator is not yet supported.

The types supported are a slightly different mix to the format() types.
Some format() types come directly over: d, n, f, b, o, h, x and X.
In addition some regular expression character group types
D, w, W, s and S are also available.

The format() types %, F, e, E, g and G are not yet supported.

===== ========================================== =======
Type  Characters Matched                         Output
===== ========================================== =======
 w    Letters and underscore                     str
 W    Non-letter and underscore                  str
 s    Whitespace                                 str
 S    Non-whitespace                             str
 d    Digits (effectively integer numbers)       int
 D    Non-digit                                  str
 n    Numbers with thousands separators (, or .) int
 f    Fixed-point numbers                        float
 b    Binary numbers                             int
 o    Octal numbers                              int
 h    Hexadecimal numbers (lower and upper case) int
 x    Lower-case hexadecimal numbers             int
 X    Upper-case hexadecimal numbers             int
===== ========================================== =======

Do remember though that most often a straight type-less {} will suffice
where a more complex type specification might have been used.

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

.. _`Format String Syntax`: http://docs.python.org/library/string.html#format-string-syntax
.. _`Format Specification Mini-Language`: http://docs.python.org/library/string.html#format-specification-mini-language

----

**Version history (in brief)**:

- 1.1.3 type conversion is automatic based on specified field types. Also added
  "f" and "n" types.
- 1.1.2 refactored, added compile() and limited ``from parse import *``
- 1.1.1 documentation improvements
- 1.1.0 implemented more of the `Format Specification Mini-Language`_
  and removed the restriction on mixing fixed-position and named fields
- 1.0.0 initial release

This code is copyright 2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
