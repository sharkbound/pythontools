import datatypes
import constants
import enums


def assign_operator_type(value: datatypes.ValueWithIndexShift):
    if value.value_as_str in constants.str_to_operator_type:
        value = value.assign_operator_type(constants.str_to_operator_type[value.value_as_str])
    return value
