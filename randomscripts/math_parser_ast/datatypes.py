from dataclasses import dataclass, replace
from typing import NamedTuple
import enums

PeekProgress = NamedTuple('PeekAheadProgress', (
    ('value', str),
    ('prev_chars', list[str]),
    ('prev_str', str),
    ('full_str', str),
    ('full_chars', list[str])
))


@dataclass(frozen=True)
class ValueWithIndexShift:
    value: tuple[str]
    start_index: int
    end_index: int
    success: bool
    type: enums.TokenType = enums.TokenType.NOT_SET
    operator_type: enums.OperatorType = enums.OperatorType.NOT_SET

    @property
    def value_as_str(self):
        return ''.join(self.value)

    @property
    def offset(self):
        return self.end_index - self.start_index

    @property
    def is_known_type(self):
        return self.type not in (enums.TokenType.NOT_SET, enums.TokenType.INVALID)

    def assign_type(self, token_type: enums.TokenType):
        return replace(self, type=token_type)

    def assign_operator_type(self, operator_type: enums.OperatorType):
        return replace(self, operator_type=operator_type)


VALUE_WITH_INDEX_SHIFT_INVALID = ValueWithIndexShift(value=(), start_index=-1, end_index=-1, success=False, type=enums.TokenType.INVALID)
VALUE_WITH_INDEX_SHIFT_NOT_SET = ValueWithIndexShift(value=(), start_index=-1, end_index=-1, success=False, type=enums.TokenType.NOT_SET)
