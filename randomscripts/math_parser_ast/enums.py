from enum import IntFlag, auto, Enum


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


class OperatorType(Enum):
    NOT_SET = auto()
    # equality
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()
    # math
    MUL = auto()
    ADD = auto()
    SUB = auto()
    DIV = auto()
    POWER = auto()
    # grouping
    GROUPING_START = auto()
    GROUPING_END = auto()

    @property
    def is_set(self):
        return self is not OperatorType.NOT_SET


def get_bit_flags(value, enum_cls):
    return {flag for flag in enum_cls if value & flag == flag}
