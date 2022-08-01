import re
import enums
from string import ascii_letters

MATH_CHARS = set('*/-+^')
EQUALITY_CHARS = set('=!<>')
GROUPING_CHARS = set('()')
NUMBER_LITERAL_CHARS = set('01234567890-')

EQUALITY_OPERATORS = {'=', '==', '!=', '<', '>', '<=', '>='}
MATH_OPERATORS = {'*', '/', '-', '+', '^'}

ALL_OPERATOR_CHARS = MATH_CHARS | EQUALITY_CHARS | GROUPING_CHARS
ALL_VARIABLE_CHARS = set(ascii_letters) | {'_'}

ALL_OPERATORS = MATH_OPERATORS | EQUALITY_OPERATORS | GROUPING_CHARS

RE_INT = re.compile(r'^([-]?)(\d+)$')

str_to_operator_type = {
    # equality
    '<': enums.OperatorType.LESS_THAN,
    '<=': enums.OperatorType.LESS_THAN_OR_EQUAL,
    '>': enums.OperatorType.GREATER_THAN,
    '>=': enums.OperatorType.GREATER_THAN_OR_EQUAL,
    '!=': enums.OperatorType.NOT_EQUAL,
    '=': enums.OperatorType.EQUAL,
    '==': enums.OperatorType.EQUAL,
    # math
    '-': enums.OperatorType.SUB,
    '+': enums.OperatorType.ADD,
    '/': enums.OperatorType.DIV,
    '^': enums.OperatorType.POWER,
    '*': enums.OperatorType.MUL,
    # grouping
    '(': enums.OperatorType.GROUPING_START,
    ')': enums.OperatorType.GROUPING_END,

}

str_to_token_type = {
    # equality
    '<': enums.TokenType.EQUALITY_OPERATOR,
    '<=': enums.TokenType.EQUALITY_OPERATOR,
    '>': enums.TokenType.EQUALITY_OPERATOR,
    '>=': enums.TokenType.EQUALITY_OPERATOR,
    '!=': enums.TokenType.EQUALITY_OPERATOR,
    '=': enums.TokenType.EQUALITY_OPERATOR,
    '==': enums.TokenType.EQUALITY_OPERATOR,
    # math
    '-': enums.TokenType.MATH_OPERATOR,
    '+': enums.TokenType.MATH_OPERATOR,
    '/': enums.TokenType.MATH_OPERATOR,
    '^': enums.TokenType.MATH_OPERATOR,
    '*': enums.TokenType.MATH_OPERATOR,
    # grouping
    '(': enums.TokenType.GROUPING_OPERATOR,
    ')': enums.TokenType.GROUPING_OPERATOR,
}
