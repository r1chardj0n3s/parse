Parse strings using a specification based on the Python format() syntax.

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

This code is copyright 2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
