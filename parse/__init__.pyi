import re
from typing import Any, Callable, Generic, Literal, Protocol, Self, TypeVar, overload


__all__ = ['parse', 'search', 'findall', 'with_pattern']

_T = TypeVar('_T')

class _TypeConverter[_T](Protocol):
	def __call__(self, string: str) -> _T: ...


_TTypeConverter = TypeVar('_TTypeConverter', bound='_TypeConverter[Any]')


def with_pattern(pattern: str, regex_group_count=None) -> Callable[[_TTypeConverter], _TTypeConverter]: ...


class Result:
	fixed: tuple[Any, ...]
	named: dict[str, Any]
	spans: dict[int|str, tuple[int, int]]

	def __init__(self, fixed: tuple[Any, ...], named: dict[str, Any], spans: dict[int|str, tuple[int, int]]) -> None: ...
	def __getitem__(self, item) -> Any: ...
	def __contains__(self, name) -> bool: ...


class Match:
	parser: "Parser"
	match: re.Match # type: ignore[type-arg]

	def __init__(self, parser: "Parser", match: re.Match) -> None: ... # type: ignore[type-arg]
	def evaluate_result(self) -> Result: ...


class ResultIterator(Generic[_T]):
	parser: "Parser"
	string: str
	pos: int
	endpos: int
	evaluate_result: bool
	def __next__(self) -> _T: ...
	next = __next__

	def __init__(self, parser: "Parser", string: str, pos: int, endpos: int | None, evaluate_result: bool = True) -> None: ...
	def __iter__(self) -> Self: ...


class TooManyFields(ValueError): ...
class RepeatedNameError(ValueError): ...


class Parser:
	def __init__(self, format, extra_types: dict[str, _TypeConverter] | None = None, case_sensitive: bool = False) -> None: ...

	@property
	def named_fields(self) -> list[str]: ...

	@property
	def fixed_fields(self) -> list[int]: ...

	@property
	def format(self) -> str: ...

	@overload
	def parse(self, string: str, evaluate_result: Literal[True] = True) -> Result | None: ...
	@overload
	def parse(self, string: str, *, evaluate_result: Literal[False]) -> Match | None: ...
	@overload
	def parse(self, string: str, evaluate_result: Literal[False]) -> Match | None: ...

	@overload
	def search(self, string: str, pos: int = 0, endpos: int | None = None, evaluate_result: Literal[True] = True) -> Result | None: ...
	@overload
	def search(self, string: str, pos: int = 0, endpos: int | None = None, *, evaluate_result: Literal[False]) -> Match | None: ...
	@overload
	def search(self, string: str, pos: int, endpos: int | None, evaluate_result: Literal[False]) -> Match | None: ...

	@overload
	def findall(self, string: str, pos: int = 0, endpos=None, extra_types: dict[str, _TypeConverter] | None = None, evaluate_result: Literal[True] = True) -> ResultIterator[Result]: ...
	@overload
	def findall(self, string: str, pos: int = 0, endpos=None, extra_types: dict[str, _TypeConverter] | None = None, *, evaluate_result: Literal[False]) -> ResultIterator[Match]: ...
	@overload
	def findall(self, string: str, pos: int, endpos: int | None, extra_types, evaluate_result: Literal[False]) -> ResultIterator[Match]: ...

	def evaluate_result(self, m: re.Match) -> Result: ... # type: ignore[type-arg]


@overload
def parse(format: str, string: str, extra_types: dict[str, _TypeConverter] | None = None, evaluate_result: Literal[True] = True, case_sensitive: bool = ...) -> Result | None: ...
@overload
def parse(format: str, string: str, extra_types: dict[str, _TypeConverter] | None = None, *, evaluate_result: Literal[False], case_sensitive: bool = ...) -> Match | None: ...
@overload
def parse(format: str, string: str, extra_types, evaluate_result: Literal[False], case_sensitive: bool = ...) -> Match | None: ...


@overload
def search(format: str, string: str, pos: int = 0, endpos: int | None = None, extra_types: dict[str, _TypeConverter] | None = None, evaluate_result: Literal[True] = True, case_sensitive: bool = False) -> Result | None: ...
@overload
def search(format: str, string: str, pos: int = 0, endpos: int | None = None, extra_types: dict[str, _TypeConverter] | None = None, *, evaluate_result: Literal[False], case_sensitive: bool = False) -> Match | None: ...
@overload
def search(format: str, string: str, pos: int, endpos: int | None, extra_types, evaluate_result: Literal[False], case_sensitive: bool = False) -> Match | None: ...


@overload
def findall(format: str, string: str, pos: int = 0, endpos=None, extra_types: dict[str, _TypeConverter] | None = None, evaluate_result: Literal[True] = True, case_sensitive: bool = False) -> ResultIterator[Result]: ...
@overload
def findall(format: str, string: str, pos: int = 0, endpos=None, extra_types: dict[str, _TypeConverter] | None = None, *, evaluate_result: Literal[False], case_sensitive: bool = False) -> ResultIterator[Match]: ...
@overload
def findall(format, string, pos, endpos, extra_types, evaluate_result: Literal[False], case_sensitive: bool = False) -> ResultIterator[Match]: ...
