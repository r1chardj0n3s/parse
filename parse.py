from __future__ import absolute_import

import logging
import re
import sys
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import tzinfo
from decimal import Decimal


__version__ = "1.20.2"
__all__ = ["parse", "search", "findall", "with_pattern"]

log = logging.getLogger(__name__)


def with_pattern(pattern, regex_group_count=None):
    r"""Attach a regular expression pattern matcher to a custom type converter
    function.

    This annotates the type converter with the :attr:`pattern` attribute.

    EXAMPLE:
        >>> import parse
        >>> @parse.with_pattern(r"\d+")
        ... def parse_number(text):
        ...     return int(text)

    is equivalent to:

        >>> def parse_number(text):
        ...     return int(text)
        >>> parse_number.pattern = r"\d+"

    :param pattern: regular expression pattern (as text)
    :param regex_group_count: Indicates how many regex-groups are in pattern.
    :return: wrapped function
    """

    def decorator(func):
        func.pattern = pattern
        func.regex_group_count = regex_group_count
        return func

    return decorator


class int_convert:
    """Convert a string to an integer.

    The string may start with a sign.

    It may be of a base other than 2, 8, 10 or 16.

    If base isn't specified, it will be detected automatically based
    on a string format. When string starts with a base indicator, 0#nnnn,
    it overrides the default base of 10.

    It may also have other non-numeric characters that we can ignore.
    """

    CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"

    def __init__(self, base=None):
        self.base = base

    def __call__(self, string, match):
        if string[0] == "-":
            sign = -1
            number_start = 1
        elif string[0] == "+":
            sign = 1
            number_start = 1
        else:
            sign = 1
            number_start = 0

        base = self.base
        # If base wasn't specified, detect it automatically
        if base is None:
            # Assume decimal number, unless different base is detected
            base = 10

            # For number formats starting with 0b, 0o, 0x, use corresponding base ...
            if string[number_start] == "0" and len(string) - number_start > 2:
                if string[number_start + 1] in "bB":
                    base = 2
                elif string[number_start + 1] in "oO":
                    base = 8
                elif string[number_start + 1] in "xX":
                    base = 16

        chars = int_convert.CHARS[:base]
        string = re.sub("[^%s]" % chars, "", string.lower())
        return sign * int(string, base)


class convert_first:
    """Convert the first element of a pair.
    This equivalent to lambda s,m: converter(s). But unlike a lambda function, it can be pickled
    """

    def __init__(self, converter):
        self.converter = converter

    def __call__(self, string, match):
        return self.converter(string)


def percentage(string, match):
    return float(string[:-1]) / 100.0


class FixedTzOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    ZERO = timedelta(0)

    def __init__(self, offset, name):
        self._offset = timedelta(minutes=offset)
        self._name = name

    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name__, self._name, self._offset)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self._name

    def dst(self, dt):
        return self.ZERO

    def __eq__(self, other):
        if not isinstance(other, FixedTzOffset):
            return NotImplemented
        return self._name == other._name and self._offset == other._offset


MONTHS_MAP = {
    "Jan": 1,
    "January": 1,
    "Feb": 2,
    "February": 2,
    "Mar": 3,
    "March": 3,
    "Apr": 4,
    "April": 4,
    "May": 5,
    "Jun": 6,
    "June": 6,
    "Jul": 7,
    "July": 7,
    "Aug": 8,
    "August": 8,
    "Sep": 9,
    "September": 9,
    "Oct": 10,
    "October": 10,
    "Nov": 11,
    "November": 11,
    "Dec": 12,
    "December": 12,
}
DAYS_PAT = r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)"
MONTHS_PAT = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
ALL_MONTHS_PAT = r"(%s)" % "|".join(MONTHS_MAP)
TIME_PAT = r"(\d{1,2}:\d{1,2}(:\d{1,2}(\.\d+)?)?)"
AM_PAT = r"(\s+[AP]M)"
TZ_PAT = r"(\s+[-+]\d\d?:?\d\d)"


def date_convert(
    string,
    match,
    ymd=None,
    mdy=None,
    dmy=None,
    d_m_y=None,
    hms=None,
    am=None,
    tz=None,
    mm=None,
    dd=None,
):
    """Convert the incoming string containing some date / time info into a
    datetime instance.
    """
    groups = match.groups()
    time_only = False
    if mm and dd:
        y = datetime.today().year
        m = groups[mm]
        d = groups[dd]
    elif ymd is not None:
        y, m, d = re.split(r"[-/\s]", groups[ymd])
    elif mdy is not None:
        m, d, y = re.split(r"[-/\s]", groups[mdy])
    elif dmy is not None:
        d, m, y = re.split(r"[-/\s]", groups[dmy])
    elif d_m_y is not None:
        d, m, y = d_m_y
        d = groups[d]
        m = groups[m]
        y = groups[y]
    else:
        time_only = True

    H = M = S = u = 0
    if hms is not None and groups[hms]:
        t = groups[hms].split(":")
        if len(t) == 2:
            H, M = t
        else:
            H, M, S = t
            if "." in S:
                S, u = S.split(".")
                u = int(float("." + u) * 1000000)
            S = int(S)
        H = int(H)
        M = int(M)

    if am is not None:
        am = groups[am]
        if am:
            am = am.strip()
        if am == "AM" and H == 12:
            # correction for "12" hour functioning as "0" hour: 12:15 AM = 00:15 by 24 hr clock
            H -= 12
        elif am == "PM" and H == 12:
            # no correction needed: 12PM is midday, 12:00 by 24 hour clock
            pass
        elif am == "PM":
            H += 12

    if tz is not None:
        tz = groups[tz]
    if tz == "Z":
        tz = FixedTzOffset(0, "UTC")
    elif tz:
        tz = tz.strip()
        if tz.isupper():
            # TODO use the awesome python TZ module?
            pass
        else:
            sign = tz[0]
            if ":" in tz:
                tzh, tzm = tz[1:].split(":")
            elif len(tz) == 4:  # 'snnn'
                tzh, tzm = tz[1], tz[2:4]
            else:
                tzh, tzm = tz[1:3], tz[3:5]
            offset = int(tzm) + int(tzh) * 60
            if sign == "-":
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


def strf_date_convert(x, _, type):
    is_date = any("%" + x in type for x in "aAwdbBmyYjUW")
    is_time = any("%" + x in type for x in "HIpMSfz")

    dt = datetime.strptime(x, type)
    if "%y" not in type and "%Y" not in type:  # year not specified
        dt = dt.replace(year=datetime.today().year)

    if is_date and is_time:
        return dt
    elif is_date:
        return dt.date()
    elif is_time:
        return dt.time()
    else:
        ValueError("Datetime not a date nor a time?")


# ref: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
dt_format_to_regex = {
    "%a": "(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)",
    "%A": "(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)",
    "%w": "[0-6]",
    "%d": "[0-9]{1,2}",
    "%b": "(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
    "%B": "(?:January|February|March|April|May|June|July|August|September|October|November|December)",
    "%m": "[0-9]{1,2}",
    "%y": "[0-9]{2}",
    "%Y": "[0-9]{4}",
    "%H": "[0-9]{1,2}",
    "%I": "[0-9]{1,2}",
    "%p": "(?:AM|PM)",
    "%M": "[0-9]{2}",
    "%S": "[0-9]{2}",
    "%f": "[0-9]{1,6}",
    "%z": "[+|-][0-9]{2}(:?[0-9]{2})?(:?[0-9]{2})?",
    # "%Z": punt
    "%j": "[0-9]{1,3}",
    "%U": "[0-9]{1,2}",
    "%W": "[0-9]{1,2}",
}

# Compile a regular expression pattern that matches any date/time format symbol.
dt_format_symbols_re = re.compile("|".join(dt_format_to_regex))


def get_regex_for_datetime_format(format_):
    """
    Generate a regex pattern for a given datetime format string.

    Parameters:
        format_ (str): The datetime format string.

    Returns:
        str: A regex pattern corresponding to the datetime format string.
    """
    # Replace all format symbols with their regex patterns.
    return dt_format_symbols_re.sub(lambda m: dt_format_to_regex[m.group(0)], format_)


class TooManyFields(ValueError):
    pass


class RepeatedNameError(ValueError):
    pass


# note: {} are handled separately
REGEX_SAFETY = re.compile(r"([?\\.[\]()*+^$!|])")

# allowed field types
ALLOWED_TYPES = set(list("nbox%fFegwWdDsSl") + ["t" + c for c in "ieahgcts"])


def extract_format(format, extra_types):
    """Pull apart the format [[fill]align][sign][0][width][.precision][type]"""
    fill = align = None
    if format[0] in "<>=^":
        align = format[0]
        format = format[1:]
    elif len(format) > 1 and format[1] in "<>=^":
        fill = format[0]
        align = format[1]
        format = format[2:]

    if format.startswith(("+", "-", " ")):
        format = format[1:]

    zero = False
    if format and format[0] == "0":
        zero = True
        format = format[1:]

    width = ""
    while format:
        if not format[0].isdigit():
            break
        width += format[0]
        format = format[1:]

    if format.startswith("."):
        # Precision isn't needed but we need to capture it so that
        # the ValueError isn't raised.
        format = format[1:]  # drop the '.'
        precision = ""
        while format:
            if not format[0].isdigit():
                break
            precision += format[0]
            format = format[1:]

    # the rest is the type, if present
    type = format
    if (
        type
        and type not in ALLOWED_TYPES
        and type not in extra_types
        and not any(k in type for k in dt_format_to_regex)
    ):
        raise ValueError("format spec %r not recognised" % type)

    return locals()


PARSE_RE = re.compile(r"({{|}}|{[\w-]*(?:\.[\w-]+|\[[^]]+])*(?::[^}]+)?})")


class Parser(object):
    """Encapsulate a format string that may be used to parse other strings."""

    def __init__(self, format, extra_types=None, case_sensitive=False):
        # a mapping of a name as in {hello.world} to a regex-group compatible
        # name, like hello__world. It's used to prevent the transformation of
        # name-to-group and group to name to fail subtly, such as in:
        # hello_.world-> hello___world->hello._world
        self._group_to_name_map = {}
        # also store the original field name to group name mapping to allow
        # multiple instances of a name in the format string
        self._name_to_group_map = {}
        # and to sanity check the repeated instances store away the first
        # field type specification for the named field
        self._name_types = {}

        self._format = format
        if extra_types is None:
            extra_types = {}
        self._extra_types = extra_types
        if case_sensitive:
            self._re_flags = re.DOTALL
        else:
            self._re_flags = re.IGNORECASE | re.DOTALL
        self._fixed_fields = []
        self._named_fields = []
        self._group_index = 0
        self._type_conversions = {}
        self._expression = self._generate_expression()
        self.__search_re = None
        self.__match_re = None

        log.debug("format %r -> %r", format, self._expression)

    def __repr__(self):
        if len(self._format) > 20:
            return "<%s %r>" % (self.__class__.__name__, self._format[:17] + "...")
        return "<%s %r>" % (self.__class__.__name__, self._format)

    @property
    def _search_re(self):
        if self.__search_re is None:
            try:
                self.__search_re = re.compile(self._expression, self._re_flags)
            except AssertionError:
                # access error through sys to keep py3k and backward compat
                e = str(sys.exc_info()[1])
                if e.endswith("this version only supports 100 named groups"):
                    raise TooManyFields(
                        "sorry, you are attempting to parse too many complex fields"
                    )
        return self.__search_re

    @property
    def _match_re(self):
        if self.__match_re is None:
            expression = r"\A%s\Z" % self._expression
            try:
                self.__match_re = re.compile(expression, self._re_flags)
            except AssertionError:
                # access error through sys to keep py3k and backward compat
                e = str(sys.exc_info()[1])
                if e.endswith("this version only supports 100 named groups"):
                    raise TooManyFields(
                        "sorry, you are attempting to parse too many complex fields"
                    )
            except re.error:
                raise NotImplementedError(
                    "Group names (e.g. (?P<name>) can "
                    "cause failure, as they are not escaped properly: '%s'" % expression
                )
        return self.__match_re

    @property
    def named_fields(self):
        return self._named_fields[:]

    @property
    def fixed_fields(self):
        return self._fixed_fields[:]

    @property
    def format(self):
        return self._format

    def parse(self, string, evaluate_result=True):
        """Match my format to the string exactly.

        Return a Result or Match instance or None if there's no match.
        """
        m = self._match_re.match(string)
        if m is None:
            return None

        if evaluate_result:
            return self.evaluate_result(m)
        else:
            return Match(self, m)

    def search(self, string, pos=0, endpos=None, evaluate_result=True):
        """Search the string for my format.

        Optionally start the search at "pos" character index and limit the
        search to a maximum index of endpos - equivalent to
        search(string[:endpos]).

        If the ``evaluate_result`` argument is set to ``False`` a
        Match instance is returned instead of the actual Result instance.

        Return either a Result instance or None if there's no match.
        """
        if endpos is None:
            endpos = len(string)
        m = self._search_re.search(string, pos, endpos)
        if m is None:
            return None

        if evaluate_result:
            return self.evaluate_result(m)
        else:
            return Match(self, m)

    def findall(
        self, string, pos=0, endpos=None, extra_types=None, evaluate_result=True
    ):
        """Search "string" for all occurrences of "format".

        Optionally start the search at "pos" character index and limit the
        search to a maximum index of endpos - equivalent to
        search(string[:endpos]).

        Returns an iterator that holds Result or Match instances for each format match
        found.
        """
        if endpos is None:
            endpos = len(string)
        return ResultIterator(
            self, string, pos, endpos, evaluate_result=evaluate_result
        )

    def _expand_named_fields(self, named_fields):
        result = {}
        for field, value in named_fields.items():
            # split 'aaa[bbb][ccc]...' into 'aaa' and '[bbb][ccc]...'
            n = field.find("[")
            if n == -1:
                basename, subkeys = field, ""
            else:
                basename, subkeys = field[:n], field[n:]

            # create nested dictionaries {'aaa': {'bbb': {'ccc': ...}}}
            d = result
            k = basename

            if subkeys:
                for subkey in re.findall(r"\[[^]]+]", subkeys):
                    d = d.setdefault(k, {})
                    k = subkey[1:-1]

            # assign the value to the last key
            d[k] = value

        return result

    def evaluate_result(self, m):
        """Generate a Result instance for the given regex match object"""
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
                value = self._type_conversions[k](groupdict[k], m)
            else:
                value = groupdict[k]

            named_fields[korig] = value

        # now figure the match spans
        spans = {n: m.span(name_map[n]) for n in named_fields}
        spans.update((i, m.span(n + 1)) for i, n in enumerate(self._fixed_fields))

        # and that's our result
        return Result(fixed_fields, self._expand_named_fields(named_fields), spans)

    def _regex_replace(self, match):
        return "\\" + match.group(1)

    def _generate_expression(self):
        parts = PARSE_RE.split(self._format)
        e = [
            (
                self._handle_field(part)
                if part and part[0] == "{" and part[-1] == "}"
                else (
                    REGEX_SAFETY.sub(self._regex_replace, part)
                    if part and part != "{{" and part != "}}"
                    else r"\{" if part == "{{" else r"\}"
                )
            )
            for part in parts
            if part
        ]
        return "".join(e)

    def _to_group_name(self, field):
        # return a version of field which can be used as capture group, even
        # though it might contain '.'
        group = (
            field.replace(".", "_")
            .replace("[", "_")
            .replace("]", "_")
            .replace("-", "_")
        )

        # make sure we don't collide ("a.b" colliding with "a_b")
        n = 1
        while group in self._group_to_name_map:
            n += 1
            if "." in field:
                group = field.replace(".", "_" * n)
            elif "_" in field:
                group = field.replace("_", "_" * n)
            elif "-" in field:
                group = field.replace("-", "_" * n)
            else:
                raise KeyError("duplicated group name %r" % (field,))

        # save off the mapping
        self._group_to_name_map[group] = field
        self._name_to_group_map[field] = group
        return group

    def _handle_field(self, field):
        field = field[1:-1]
        name, _, format = field.partition(":")

        if name and name[0].isalpha():
            if name in self._name_to_group_map:
                if self._name_types[name] != format:
                    raise RepeatedNameError(
                        f'field type {format!r} for field "{name}" does not match previous seen type {self._name_types[name]!r}'
                    )
                group = self._name_to_group_map[name]
                return rf"(?P={group})"
            else:
                group = self._to_group_name(name)
                self._name_types[name] = format
                self._named_fields.append(group)
                wrap = rf"(?P<{group}>%s)"
        else:
            self._fixed_fields.append(self._group_index)
            wrap = r"(%s)"
            group = self._group_index

        if not format:
            self._group_index += 1
            return wrap % r".+?"

        format = extract_format(format, self._extra_types)
        type = format["type"]
        is_numeric = type and type in "n%fegdobx"
        conv = self._type_conversions

        if type in self._extra_types:
            type_converter = self._extra_types[type]
            s = getattr(type_converter, "pattern", r".+?")
            regex_group_count = getattr(type_converter, "regex_group_count", 0) or 0
            self._group_index += regex_group_count
            conv[group] = convert_first(type_converter)
        else:
            type_patterns = {
                "n": (r"\d{1,3}([,.]\d{3})*", int_convert(10)),
                "b": (r"(0[bB])?[01]+", int_convert(2)),
                "o": (r"(0[oO])?[0-7]+", int_convert(8)),
                "x": (r"(0[xX])?[0-9a-fA-F]+", int_convert(16)),
                "%": (r"\d+(\.\d+)?%", percentage),
                "f": (r"\d*\.\d+", convert_first(float)),
                "F": (r"\d*\.\d+", convert_first(Decimal)),
                "e": (
                    r"\d*\.\d+[eE][-+]?\d+|nan|NAN|[-+]?inf|[-+]?INF",
                    convert_first(float),
                ),
                "g": (
                    r"\d+(\.\d+)?([eE][-+]?\d+)?|nan|NAN|[-+]?inf|[-+]?INF",
                    convert_first(float),
                ),
            }
            s, conv[group] = type_patterns.get(type, (r".+?", None))
            self._group_index += 1

        align = format["align"]
        fill = format["fill"] or " "

        if is_numeric and align == "=":
            fill = fill or "0"
            s = rf"{fill}*{s}"

        if is_numeric:
            s = rf"[-+ ]?{s}"

        if wrap:
            s = wrap % s
            self._group_index += 1

        if format["width"]:
            align = align or ">"

        if fill in r".\+?*[](){}^$":
            fill = "\\" + fill

        align_patterns = {
            "<": rf"{s}{fill}*",
            ">": rf"{fill}*{s}",
            "^": rf"{fill}*{s}{fill}*",
        }
        s = align_patterns.get(align, s)

        return s


class Result(object):
    """The result of a parse() or search().

    Fixed results may be looked up using `result[index]`.
    Slices of fixed results may also be looked up.

    Named results may be looked up using `result['name']`.

    Named results may be tested for existence using `'name' in result`.
    """

    def __init__(self, fixed, named, spans):
        self.fixed = fixed
        self.named = named
        self.spans = spans

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self.fixed[item]
        return self.named[item]

    def __repr__(self):
        return "<%s %r %r>" % (self.__class__.__name__, self.fixed, self.named)

    def __contains__(self, name):
        return name in self.named


class Match(object):
    """The result of a parse() or search() if no results are generated.

    This class is only used to expose internal used regex match objects
    to the user and use them for external Parser.evaluate_result calls.
    """

    def __init__(self, parser, match):
        self.parser = parser
        self.match = match

    def evaluate_result(self):
        """Generate results for this Match"""
        return self.parser.evaluate_result(self.match)


class ResultIterator(object):
    """The result of a findall() operation.

    Each element is a Result instance.
    """

    def __init__(self, parser, string, pos, endpos, evaluate_result=True):
        self.parser = parser
        self.string = string
        self.pos = pos
        self.endpos = endpos
        self.evaluate_result = evaluate_result

    def __iter__(self):
        return self

    def __next__(self):
        m = self.parser._search_re.search(self.string, self.pos, self.endpos)
        if m is None:
            raise StopIteration()
        self.pos = m.end()

        if self.evaluate_result:
            return self.parser.evaluate_result(m)
        else:
            return Match(self.parser, m)

    # pre-py3k compat
    next = __next__


def parse(format, string, extra_types=None, evaluate_result=True, case_sensitive=False):
    """Using "format" attempt to pull values from "string".

    The format must match the string contents exactly. If the value
    you're looking for is instead just a part of the string use
    search().

    If ``evaluate_result`` is True the return value will be an Result instance with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If ``evaluate_result`` is False the return value will be a Match instance with one method:

     .evaluate_result() - This will return a Result instance like you would get
                          with ``evaluate_result`` set to True

    The default behaviour is to match strings case insensitively. You may match with
    case by specifying case_sensitive=True.

    If the format is invalid a ValueError will be raised.

    See the module documentation for the use of "extra_types".

    In the case there is no match parse() will return None.
    """
    p = Parser(format, extra_types=extra_types, case_sensitive=case_sensitive)
    return p.parse(string, evaluate_result=evaluate_result)


def search(
    format,
    string,
    pos=0,
    endpos=None,
    extra_types=None,
    evaluate_result=True,
    case_sensitive=False,
):
    """Search "string" for the first occurrence of "format".

    The format may occur anywhere within the string. If
    instead you wish for the format to exactly match the string
    use parse().

    Optionally start the search at "pos" character index and limit the search
    to a maximum index of endpos - equivalent to search(string[:endpos]).

    If ``evaluate_result`` is True the return value will be an Result instance with two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If ``evaluate_result`` is False the return value will be a Match instance with one method:

     .evaluate_result() - This will return a Result instance like you would get
                          with ``evaluate_result`` set to True

    The default behaviour is to match strings case insensitively. You may match with
    case by specifying case_sensitive=True.

    If the format is invalid a ValueError will be raised.

    See the module documentation for the use of "extra_types".

    In the case there is no match parse() will return None.
    """
    p = Parser(format, extra_types=extra_types, case_sensitive=case_sensitive)
    return p.search(string, pos, endpos, evaluate_result=evaluate_result)


def findall(
    format,
    string,
    pos=0,
    endpos=None,
    extra_types=None,
    evaluate_result=True,
    case_sensitive=False,
):
    """Search "string" for all occurrences of "format".

    You will be returned an iterator that holds Result instances
    for each format match found.

    Optionally start the search at "pos" character index and limit the search
    to a maximum index of endpos - equivalent to search(string[:endpos]).

    If ``evaluate_result`` is True each returned Result instance has two attributes:

     .fixed - tuple of fixed-position values from the string
     .named - dict of named values from the string

    If ``evaluate_result`` is False each returned value is a Match instance with one method:

     .evaluate_result() - This will return a Result instance like you would get
                          with ``evaluate_result`` set to True

    The default behaviour is to match strings case insensitively. You may match with
    case by specifying case_sensitive=True.

    If the format is invalid a ValueError will be raised.

    See the module documentation for the use of "extra_types".
    """
    p = Parser(format, extra_types=extra_types, case_sensitive=case_sensitive)
    return p.findall(string, pos, endpos, evaluate_result=evaluate_result)


def compile(format, extra_types=None, case_sensitive=False):
    """Create a Parser instance to parse "format".

    The resultant Parser has a method .parse(string) which
    behaves in the same manner as parse(format, string).

    The default behaviour is to match strings case insensitively. You may match with
    case by specifying case_sensitive=True.

    Use this function if you intend to parse many strings
    with the same format.

    See the module documentation for the use of "extra_types".

    Returns a Parser instance.
    """
    return Parser(format, extra_types=extra_types, case_sensitive=case_sensitive)


# Copyright (c) 2012-2020 Richard Jones <richard@python.org>
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
