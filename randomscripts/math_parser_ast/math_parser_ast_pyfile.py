import re
from dataclasses import dataclass, field
from enum import auto, IntFlag
from string import ascii_letters
from types import SimpleNamespace
from typing import NamedTuple, Optional

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

    @property
    def is_set(self):
        return self not in (self.NOT_SET, self.INVALID)

    def has_flags(self, flag):
        return (self & flag) == flag


MATH_CHARS = set('*/-+^')
EQUALITY_CHARS = set('=!<>')
GROUPING_CHARS = set('()')
NUMBER_LITERAL_CHARS = set('01234567890-+')

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
        return (self.end_index - self.start_index) or 1

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
    peeked = peek_ahead(data, i, lambda x, _: x in ALL_OPERATOR_CHARS)
    return peeked.value_as_str in ALL_OPERATORS or is_grouping_operator(data[i])


def is_number_literal(data, i):
    value = peek_ahead(data, i, lambda x, items: RE_INT.match(''.join(items)))
    return value.success and RE_INT.match(value.value_as_str)


def _read_and_assign_type_if_success(data, i, predicate, type_if_success, limit=None):
    value = peek_ahead(data, i, predicate, limit=limit)
    if value.success:
        return value._replace(type=type_if_success)
    return ValueWithIndexShift.invalid()


def read_variable(data, index):
    return _read_and_assign_type_if_success(data, index, lambda x, _: x in ALL_VARIABLE_CHARS, ValueType.VARIABLE)


_grouping_char_to_type = {'(': ValueType.GROUPING_START_OPERATOR, ')': ValueType.GROUPING_END_OPERATOR}


def read_operator(data, index):
    value = _read_and_assign_type_if_success(
        data=data,
        i=index,
        predicate=lambda x, _: x in ALL_OPERATOR_CHARS,
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
    value = _read_and_assign_type_if_success(data, index, lambda x, _: x in NUMBER_LITERAL_CHARS,
                                             ValueType.INT_LITERAL)
    if value.success and RE_INT.match(value.value_as_str):
        return value

    return ValueWithIndexShift.invalid()


def peek_ahead(data, index, predicate, limit=None):
    chars = []
    original_index = index
    while (limit is None or limit > 0) and index < len(data) and predicate(data[index], chars):
        chars.append(data[index])
        index += 1
        if limit is not None:
            limit -= 1

    return ValueWithIndexShift(
        value=tuple(chars),
        start_index=original_index,
        end_index=index,
        success=bool(chars),
        type=ValueType.NOT_SET
    )


def handle_char(char, data, i):
    if is_variable_char(char):
        return read_variable(data, i)

    if is_number_literal(data, i):
        return read_literal(data, i)

    if is_operator_sequence(data, i):
        return read_operator(data, i)

    return ValueWithIndexShift.invalid()


@dataclass()
class GroupingContainer:
    start: int
    end: int
    items: list['GroupingContainer | ValueWithIndexShift']
    parent: Optional['GroupingContainer'] = field(repr=False, default=None)
    start_symbol: Optional['ValueWithIndexShift'] = field(repr=False, default=None)
    end_symbol: Optional['ValueWithIndexShift'] = field(repr=False, default=None)

    @classmethod
    def empty(cls):
        return cls(-1, -1, [])

    @classmethod
    def starting_at(cls, start: int):
        empty = cls.empty()
        empty.start = start
        return empty

    @property
    def has_parent(self):
        return self.parent is not None

    def with_parent(self, new_parent: Optional['GroupingContainer']):
        if new_parent is not None and new_parent.start != -1:
            self.parent = new_parent
        return self


def _create_grouping(start: int, end: int, subitems: list):
    return SimpleNamespace(start=start, end=end, subitems=subitems)


def flatten_symbols(symbols: list):
    for symbol in symbols:
        match symbol:
            case ValueWithIndexShift():
                yield symbol
            case GroupingContainer():
                yield from flatten_symbols(symbol.items)


def _handle_grouping(value, current_grouping: GroupingContainer, completed_groupings: list, data: list = None):
    if value.type & ValueType.GROUPING_START:
        if current_grouping.start == -1:
            new_group = GroupingContainer.starting_at(value.start_index).with_parent(current_grouping)
            new_group.start_symbol = value
        else:
            new_group = GroupingContainer.starting_at(value.start_index).with_parent(current_grouping)
            new_group.start_symbol = value
            current_grouping.items.append(new_group)
        return new_group, completed_groupings

    elif value.type & ValueType.GROUPING_END:
        if current_grouping.start == -1:
            error = f'\ncannot end grouping at index: {value.start_index}, there is no currently open grouping to close\n\n'
            if data is not None:
                error += ''.join(data)
                error += '\n' + '-' * value.start_index + '^'
            raise RuntimeError(error)

        current_grouping.end_symbol = value
        current_grouping.end = value.start_index
        prev_grouping = current_grouping.parent if current_grouping.has_parent else GroupingContainer.empty()
        completed_groupings.append(current_grouping)
        return prev_grouping, completed_groupings

    return current_grouping, completed_groupings


def parse_math(equation):
    current_grouping = GroupingContainer.empty()
    completed_groupings = []
    parsed_values = []
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

        # if ret.type & ValueType.GROUPING_OPERATOR:
        #     current_grouping, completed_groupings = _handle_grouping(
        #         ret, current_grouping, completed_groupings, data=equation)
        #     if current_grouping.start != -1:
        #         parsed_values.append(current_grouping)
        # else:
        #     if current_grouping.start != -1:
        #         current_grouping.items.append(ret)
        #     else:
        #         parsed_values.append(ret)
        parsed_values.append(ret)
        i += ret.offset

    return parsed_values


symbols = parse_math('(1+y)== 2')
ic(list(flatten_symbols(symbols)))
