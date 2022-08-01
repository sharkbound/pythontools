import re
from collections import defaultdict

from icecream import ic
import datatypes
import constants
import readutils
import enums
import checking
import predicates
import utils


def handle_char(char, data, i):
    if checking.is_int_literal(char):
        return readutils.read_int(data, i)

    if checking.is_operator(char):
        peek_result = readutils.peek_ahead(data, i, predicates.pred_is_operator)
        return utils.assign_operator_type(
            value=peek_result.assign_type(
                token_type=constants.str_to_token_type[peek_result.value_as_str]
            )
        )

    return datatypes.ValueWithIndexShift.invalid()


def are_symbols_adjacent(left: datatypes.ValueWithIndexShift, right: datatypes.ValueWithIndexShift):
    return left.end_index == right.start_index


def parse_math(equation):
    flag_index = defaultdict(list)
    symbols = []
    equation = list(re.sub(r'\s+', ' ', equation))
    i = 0
    while i < len(equation):
        char = equation[i]

        ret = handle_char(char, equation, i)
        if not ret.is_known_type:
            i += 1
            continue

        symbols.append(ret)
        i += ret.offset
        for flag in enums.get_bit_flags(ret.type, enums.TokenType):
            flag_index[flag].append(ret)

    return symbols, flag_index


symbols, flag_index = parse_math('<=>===!=')
for symbol in symbols:
    print(f'{symbol.value_as_str=!r:<10} | {symbol.type.name=:<20} | {symbol.operator_type.name=:<10}')
