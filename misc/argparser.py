from itertools import zip_longest
from typing import Callable, Any, Sized, Sequence


class ArgParserResult:
    def __init__(self, validators: Sequence[Callable], names: Sequence[str], args: Sequence[Any]):
        self.names = names
        self.validators = validators
        self.raw_args = args

        self.named_args = {}
        self.invalid_args = {}
        self.unnamed_args = []

        self.named_errors = {}

        self._parse()

    @property
    def has_invalid_args(self):
        return bool(self.invalid_args)

    @property
    def invalid_arg_names(self):
        return tuple(self.invalid_args)

    def get_error(self, arg_name):
        return self.named_errors.get(arg_name)

    def get_args(self, *arg_names: str):
        return [self[arg] for arg in arg_names]

    def _parse(self):
        for callable, name, value in zip_longest(self.validators, self.names, self.raw_args):
            if callable is None:
                self.unnamed_args.append(value)
                continue

            if name is None:
                self.unnamed_args.append(value)
                continue

            try:
                self.named_args[name] = callable(value)
            except Exception as e:
                self.invalid_args[name] = value
                self.named_errors[name] = e

    def __getattr__(self, item):
        if isinstance(item, str):
            if item in self.named_args:
                return self.named_args[item]

            if item in self.invalid_args:
                return self.invalid_args[item]

        if isinstance(item, (int, slice)):
            try:
                return self.unnamed_args[item]
            except:
                pass
        return None

    __getitem__ = __getattr__

    def __repr__(self):
        return f'<{type(self).__name__} valid={self.named_args} invalid={self.invalid_args} unnamed_args={self.unnamed_args}>'


class ArgParser:
    def __init__(self, validators: Sequence[Callable], names: Sequence[str]):
        self.validators = validators
        self.names = names

    def parse(self, args: Sequence[Any]):
        return ArgParserResult(self.validators, self.names, args)


if __name__ == '__main__':
    parser = ArgParser([int, int, int], ['a', 'b', 'c'])
    args = parser.parse(('1', 'b', '2', '4', 7, 9))

    from icecream import ic

    ic(args.get_args('a', 'b'))
    ic(args.a, args.b, args.c)
