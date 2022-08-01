from dataclasses import replace

from datatypes import PeekProgress, ValueWithIndexShift
from constants import NUMBER_LITERAL_CHARS, RE_INT, ALL_VARIABLE_CHARS
from enums import TokenType


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
    )


def read_and_assign_type_if_success(data, i, predicate, type_if_success, limit=None):
    value = peek_ahead(data, i, predicate, limit=limit)
    if value.success:
        return value.assign_type(type_if_success)
    return ValueWithIndexShift.invalid()


def read_variable(data, index):
    return read_and_assign_type_if_success(data, index, lambda x: x.value in ALL_VARIABLE_CHARS, TokenType.VARIABLE)


def read_literal(data, index):
    if data[index].isspace():
        return read_and_assign_type_if_success(data, index, lambda x: x.value.isspace(), TokenType.SPACE)

    def _read(x: PeekProgress):
        if x.value not in NUMBER_LITERAL_CHARS:
            return False
        if x.value.isnumeric():
            return True
        return x.value == '-' and not x.prev_chars

    value = read_and_assign_type_if_success(data, index, _read, TokenType.INT_LITERAL)
    if value.success and RE_INT.match(value.value_as_str):
        return value

    return ValueWithIndexShift.invalid()


def read_int(data, index):
    return read_and_assign_type_if_success(data, index, lambda x: x.value.isnumeric(), TokenType.INT_LITERAL)
