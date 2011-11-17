Parse strings using a specification based on the Python format() syntax.

   parse() is the opposite of format()

The `Format String Syntax`_ is supported with anonymous (fixed-position),
named and formatted values are supported::

   {[field name]:[format spec]}

Field names must be a single Python identifier word. No attributes or
element indexes are supported (as they would make no sense.)

Numbered fields are also not supported: the result of parsing will include
the parsed fields in the order they are parsed.

There conversion of values to types other than strings is not yet supported.

Some simple parse() format string examples:

 >>> parse("Bring me a {}", "Bring me a shrubbery")
 <Result ('shrubbery',) {}>
 >>> parse("The {} who say {}", "The knights who say Ni!")
 <Result ('knights', 'Ni!') {}>
 >>> parse("Bring out the holy {item}", "Bring out the holy hand grenade")
 <Result () {'item': 'hand grenade'}>

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

This code is copyright 2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
