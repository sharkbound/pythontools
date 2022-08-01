import readutils
import constants


def is_int_literal(value):
    return value.isnumeric()


def is_operator(value):
    return value in constants.ALL_OPERATOR_CHARS
