import constants
import datatypes


# def pred_is_operator(value: datatypes.PeekProgress):
#     if len(value.full_chars) == 1:
#         return value.value in constants.ALL_OPERATOR_CHARS
#     return value.full_str in constants.ALL_OPERATORS


def pred_is_operator_char(value: datatypes.PeekProgress):
    return value.value in constants.ALL_OPERATOR_CHARS
