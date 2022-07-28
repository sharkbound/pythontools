import re
from collections import namedtuple
from enum import Flag, auto, Enum, IntFlag
from pprint import pprint
from string import ascii_letters
from typing import NamedTuple

from icecream import ic


class ValueType(IntFlag):
    INVALID = auto()
    NOT_SET = auto()

    VARIABLE = auto()
    LITERAL = auto()
    INT = auto()
    FLOAT = auto()

    INT_LITERAL = INT | LITERAL
    FLOAT_LITERAL = FLOAT | LITERAL

    GROUPING = auto()
    GROUPING_START = auto()
    GROUPING_END = auto()

    OPERATOR = auto()
    MATH_OPERATION = auto()
    EQUALITY = auto()

    EQUALITY_OPERATOR = OPERATOR | EQUALITY
    GROUPING_OPERATOR = OPERATOR | GROUPING
    GROUPING_START_OPERATOR = GROUPING_OPERATOR | GROUPING_START | GROUPING
    GROUPING_END_OPERATOR = GROUPING_OPERATOR | GROUPING_END | GROUPING
    MATH_OPERATOR = OPERATOR | MATH_OPERATION


MATH_CHARS = set('*/-+^')
EQUALITY_CHARS = set('=!<>')
GROUPING_CHARS = set('()')
NUMBER_LITERAL_CHARS = set('01234567890-')

EQUALITY_OPERATORS = {'==', '!=', '<', '>', '<=', '>='}
MATH_OPERATORS = {'*', '/', '-', '+', '^'}

ALL_OPERATOR_CHARS = MATH_CHARS | EQUALITY_CHARS | GROUPING_CHARS
ALL_VARIABLE_CHARS = set(ascii_letters) | {'_'}

ALL_OPERATORS = MATH_OPERATORS | EQUALITY_OPERATORS

RE_INT = re.compile(r'^([-]?)(\d+)$')


class ValueWithIndexShift(NamedTuple):
    value: tuple[str]
    start_index: int
    end_index: int
    success: bool
    type: ValueType = ValueType.NOT_SET

    @property
    def islist(self):
        return isinstance(self.value, list)

    @property
    def isstr(self):
        return isinstance(self.value, str)

    @property
    def value_as_str(self):
        return ''.join(self.value)

    @property
    def offset(self):
        return self.end_index - self.start_index

    @classmethod
    def not_set(cls):
        return cls(value=(), start_index=-1, end_index=-1, success=False, type=ValueType.NOT_SET)

    @classmethod
    def invalid(cls):
        return cls(value=(), start_index=-1, end_index=-1, success=False, type=ValueType.INVALID)


def values_index_shift_to_friendly_str(*values: ValueWithIndexShift):
    for value in values:
        yield f'<ValueWithIndexShift VALUE={value.value_as_str!r} TYPE={value.type!r}>'


def is_variable_char(char):
    return char in ALL_VARIABLE_CHARS


def is_grouping_operator(char):
    return char in GROUPING_CHARS


def is_operator_sequence(data, i):
    peeked = peek_ahead(data, i, lambda x: x.full_str in ALL_OPERATORS)
    return peeked.success or is_grouping_operator(data[i])


def _impl_is_literal_check(value: 'PeekAheadProgress'):
    if value.value == '-':
        return not value.prev_chars and '-' not in value.prev_chars
    return value.value.isnumeric()


def is_literal(data, i):
    value = peek_ahead(data, i, _impl_is_literal_check)
    return value.success and RE_INT.match(value.value_as_str)


def _read_and_assign_type_if_success(data, i, predicate, type_if_success, limit=None):
    value = peek_ahead(data, i, predicate, limit=limit)
    if value.success:
        return value._replace(type=type_if_success)
    return ValueWithIndexShift.invalid()


def read_variable(data, index):
    return _read_and_assign_type_if_success(data, index, lambda x: x.value in ALL_VARIABLE_CHARS, ValueType.VARIABLE)


_grouping_char_to_type = {'(': ValueType.GROUPING_START_OPERATOR, ')': ValueType.GROUPING_END_OPERATOR}


def read_operator(data, index):
    value = _read_and_assign_type_if_success(
        data=data,
        i=index,
        predicate=lambda x: x.full_str in ALL_OPERATORS,
        type_if_success=ValueType.OPERATOR,
        limit=(1 if data[index] in GROUPING_CHARS else None)
    )

    value_as_string = value.value_as_str

    if value_as_string in EQUALITY_OPERATORS:
        return value._replace(type=ValueType.EQUALITY_OPERATOR)

    if value_as_string in MATH_OPERATORS:
        return value._replace(type=ValueType.MATH_OPERATOR)

    if value_as_string in GROUPING_CHARS:
        return value._replace(type=_grouping_char_to_type[value_as_string])

    return ValueWithIndexShift.invalid()


def read_literal(data, index):
    def _read(x: PeekAheadProgress):
        if x.value not in NUMBER_LITERAL_CHARS:
            return False
        if x.value.isnumeric():
            return True
        return x.value == '-' and not x.prev_chars

    value = _read_and_assign_type_if_success(data, index, _read, ValueType.INT_LITERAL)
    if value.success and RE_INT.match(value.value_as_str):
        return value

    return ValueWithIndexShift.invalid()


PeekAheadProgress = NamedTuple('PeekAheadProgress', (
    ('value', str),
    ('prev_chars', list[str]),
    ('prev_str', str),
    ('full_str', str),
    ('full_chars', list[str])
))


def peek_ahead(data, index, predicate, limit=None):
    prev_chars: list[str] = []
    original_index = index
    while (
            (limit is None or limit > 0)
            and index < len(data)
            and predicate(PeekAheadProgress(
        value=data[index],
        prev_chars=prev_chars,
        prev_str=''.join(prev_chars),
        full_str=(fullstr := (''.join(prev_chars) + data[index])),
        full_chars=list(fullstr)))
    ):
        prev_chars.append(data[index])
        index += 1
        if limit is not None:
            limit -= 1

    return ValueWithIndexShift(
        value=tuple(prev_chars),
        start_index=original_index,
        end_index=index,
        success=bool(prev_chars),
        type=ValueType.NOT_SET
    )


def handle_char(char, data, i):
    if is_variable_char(char):
        return read_variable(data, i)

    if is_literal(data, i):
        return read_literal(data, i)

    if is_operator_sequence(data, i):
        return read_operator(data, i)

    return ValueWithIndexShift.invalid()


def parse_math(equation):
    groupings = []
    equation = list(re.sub(r'\s+', ' ', equation))
    i = 0
    while i < len(equation):
        char = equation[i]
        if char.isspace():
            i += 1
            continue

        ret = handle_char(char, equation, i)
        if not ret.success:
            i += 1
            continue

        groupings.append(ret)
        i += ret.offset

    return groupings


symbols = parse_math('---1')
pprint(symbols)
"""
[ValueWithIndexShift(value=('-',), start_index=0, end_index=1, success=True, type=<ValueType.MATH_OPERATOR: 1536>),
 ValueWithIndexShift(value=('-',), start_index=1, end_index=2, success=True, type=<ValueType.MATH_OPERATOR: 1536>),
 ValueWithIndexShift(value=('-', '1'), start_index=2, end_index=4, success=True, type=<ValueType.INT_LITERAL: 24>)]
"""
