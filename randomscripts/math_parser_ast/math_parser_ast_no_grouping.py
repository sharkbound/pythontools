import re
from collections import namedtuple, defaultdict
from enum import Flag, auto, IntFlag
from pprint import pprint
from string import ascii_letters
from typing import NamedTuple

from icecream import ic


class TokenType(IntFlag):
    # unknown
    INVALID = auto()
    NOT_SET = auto()
    # basic
    VARIABLE = auto()
    LITERAL = auto()
    INT = auto()
    FLOAT = auto()
    SPACE = auto()
    # grouping base
    GROUPING = auto()
    # operator base
    OPERATOR = auto()
    MATH_OPERATION = auto()
    EQUALITY = auto()
    # literals
    INT_LITERAL = INT | LITERAL
    FLOAT_LITERAL = FLOAT | LITERAL
    # math
    MATH_OPERATOR = OPERATOR | MATH_OPERATION
    # equality
    EQUALITY_OPERATOR = OPERATOR | EQUALITY
    # grouping
    GROUPING_OPERATOR = OPERATOR | GROUPING


MATH_CHARS = set('*/-+^')
EQUALITY_CHARS = set('=!<>')
GROUPING_CHARS = set('()')
NUMBER_LITERAL_CHARS = set('01234567890-')

EQUALITY_OPERATORS = {'=', '!=', '<', '>', '<=', '>='}
MATH_OPERATORS = {'*', '/', '-', '+', '^'}

ALL_OPERATOR_CHARS = MATH_CHARS | EQUALITY_CHARS | GROUPING_CHARS
ALL_VARIABLE_CHARS = set(ascii_letters) | {'_'}

ALL_OPERATORS = MATH_OPERATORS | EQUALITY_OPERATORS | GROUPING_CHARS

RE_INT = re.compile(r'^([-]?)(\d+)$')


class ValueWithIndexShift(NamedTuple):
    value: tuple[str]
    start_index: int
    end_index: int
    success: bool
    type: TokenType = TokenType.NOT_SET

    @property
    def value_as_str(self):
        return ''.join(self.value)

    @property
    def offset(self):
        return self.end_index - self.start_index

    @classmethod
    def not_set(cls):
        return cls(value=(), start_index=-1, end_index=-1, success=False, type=TokenType.NOT_SET)

    @classmethod
    def invalid(cls):
        return cls(value=(), start_index=-1, end_index=-1, success=False, type=TokenType.INVALID)


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


def _impl_is_literal_check(value: 'PeekProgress'):
    if value.value == '-':
        return not value.prev_chars and '-' not in value.prev_chars
    return value.value.isnumeric()


def is_literal(data, i):
    if data[i].isspace():
        return True
    value = peek_ahead(data, i, _impl_is_literal_check)
    return value.success and RE_INT.match(value.value_as_str)


def _read_and_assign_type_if_success(data, i, predicate, type_if_success, limit=None):
    value = peek_ahead(data, i, predicate, limit=limit)
    if value.success:
        return value._replace(type=type_if_success)
    return ValueWithIndexShift.invalid()


def read_variable(data, index):
    return _read_and_assign_type_if_success(data, index, lambda x: x.value in ALL_VARIABLE_CHARS, TokenType.VARIABLE)


def read_operator(data, index):
    value = _read_and_assign_type_if_success(
        data=data,
        i=index,
        predicate=lambda x: x.full_str in ALL_OPERATORS,
        type_if_success=TokenType.OPERATOR,
        limit=(1 if data[index] in GROUPING_CHARS else None)
    )

    value_as_string = value.value_as_str

    if value_as_string in EQUALITY_OPERATORS:
        return value._replace(type=TokenType.EQUALITY_OPERATOR)

    if value_as_string in MATH_OPERATORS:
        return value._replace(type=TokenType.MATH_OPERATOR)

    if value_as_string in GROUPING_CHARS:
        return value._replace(type=TokenType.GROUPING_OPERATOR)

    return ValueWithIndexShift.invalid()


def read_literal(data, index):
    if data[index].isspace():
        return _read_and_assign_type_if_success(data, index, lambda x: x.value.isspace(), TokenType.SPACE)

    def _read(x: PeekProgress):
        if x.value not in NUMBER_LITERAL_CHARS:
            return False
        if x.value.isnumeric():
            return True
        return x.value == '-' and not x.prev_chars

    value = _read_and_assign_type_if_success(data, index, _read, TokenType.INT_LITERAL)
    if value.success and RE_INT.match(value.value_as_str):
        return value

    return ValueWithIndexShift.invalid()


PeekProgress = NamedTuple('PeekAheadProgress', (
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
            and predicate(PeekProgress(
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
        type=TokenType.NOT_SET
    )


def handle_char(char, data, i):
    if is_variable_char(char):
        return read_variable(data, i)

    if is_operator_sequence(data, i):
        return read_operator(data, i)

    if is_literal(data, i):
        return read_literal(data, i)

    return ValueWithIndexShift.invalid()


def get_bit_flags(value, enum_cls):
    return {flag for flag in enum_cls if value & flag == flag}


def are_symbols_adjacent(left: ValueWithIndexShift, right: ValueWithIndexShift):
    return left.end_index == right.start_index


# %%

def _combine_check_for_negatives(symbols: list[ValueWithIndexShift]):
    return symbols


def _combine_equality_operators(symbols: list[ValueWithIndexShift], flag_index: dict[TokenType, ValueWithIndexShift]):
    out = symbols.copy()
    i = 0
    while i < len(out):
        v = out[i]
        if not v.type & TokenType.EQUALITY_OPERATOR:
            pass
        else:
            pass
        i += 1

    return out


def combine_symbols(symbols: list[ValueWithIndexShift], flag_index: dict[TokenType, ValueWithIndexShift]):
    symbols = _combine_equality_operators(symbols, flag_index)
    return symbols


def parse_math(equation):
    flag_index = defaultdict(list)
    symbols = []
    equation = list(re.sub(r'\s+', ' ', equation))
    i = 0
    while i < len(equation):
        # todo: fix iterating missing the last element
        char = equation[i]

        ret = handle_char(char, equation, i)
        if not ret.success:
            i += 1
            continue

        symbols.append(ret)
        i += ret.offset
        for flag in get_bit_flags(ret.type, TokenType):
            flag_index[flag].append(ret)

    return symbols, flag_index


symbols, flag_index = parse_math('1 < 2 !=')
combined = combine_symbols(symbols, flag_index)
ic(combined)
# ic(flag_index[ValueType.SPACE])
# for s1, s2 in zip(symbols, symbols[1:]):
#     ic(s1, s2, are_symbols_adjacent(s1, s2))
