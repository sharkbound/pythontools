import re
from collections import deque, UserDict
from dataclasses import dataclass
from decimal import Decimal
from typing import Generator

import questionary


class Constants:
    MAX_TOPPINGS = 4
    TOPPINGS = ['lettuce', 'mayo', 'cheese', 'rice', 'tomato', 'hot sauce', 'queso']
    MEATS = ['pork', 'extra pork + $1.00', 'beef', 'extra beef + $1.00']
    SHELLS = ['hard shell', 'soft shell', 'crispy nacho shell + $1.00']
    BASE_TACO_PRICE = 10
    TACO_PARENT_KEY = 'Taco'


def to_decimal(value):
    return Decimal(str(value))


class MetaDataNode(UserDict):
    def __init__(self, meta: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.meta = meta if meta is not None else {}

    def set_price(self, price):
        self.meta['price'] = price
        return self


class Receipt:
    @dataclass
    class ItemInfo:
        __slots__ = ('name', 'value', 'depth', 'is_item', 'is_parent', 'price', 'has_price')
        name: str
        value: 'MetaDataNode'
        depth: int
        is_item: bool
        is_parent: bool
        price: Decimal
        has_price: bool

    def __init__(self):
        self.data = MetaDataNode()

    def _get_and_ensure_key_path(self, data, keys):
        for key in keys:
            if key not in data:
                data[key] = MetaDataNode({'is_parent': True})
            data = data[key]
        return data

    def add_parent(self, name, prefix_keys=()):
        return self._get_and_ensure_key_path(self.data, (*prefix_keys, name))

    def append(self, name, price=None, prefix_keys=()):
        node = self._get_and_ensure_key_path(self.data, prefix_keys)
        node[name] = MetaDataNode(
            {'price': price} if price is not None else {}
        )
        return node

    def iter_items(self) -> Generator['ItemInfo', None, None]:
        queue = deque((k, v, 0) for k, v in self.data.items())
        while queue:
            key, value, depth = queue.pop()

            is_parent = value.meta.get('is_parent', False)
            price = value.meta.get('price', -1)
            iteminfo = self.ItemInfo(
                name=key, value=value, depth=depth, is_item=price >= 0,
                is_parent=is_parent, price=max(to_decimal(0), price), has_price=price >= 0
            )
            yield iteminfo

            if is_parent:
                queue.extendleft((k, v, depth + 1) for k, v in value.items())


def topping_validator(chooses):
    if len(chooses) > Constants.MAX_TOPPINGS:
        return f'Cannot select more than {Constants.MAX_TOPPINGS} toppings!'
    return True


def handle_additional_price_selection(receipt: Receipt, args, prefix_keys=()):
    if len(args) >= 2:
        receipt.append(f'+ {args[0].strip()}', to_decimal(re.sub(r'[^0-9.]', '', args[1])), prefix_keys=prefix_keys)
    else:
        receipt.append(f'~ {args[0].strip()}', prefix_keys=prefix_keys)


def ask_for_taco():
    receipt = Receipt()
    receipt.add_parent(Constants.TACO_PARENT_KEY).set_price(Constants.BASE_TACO_PRICE)

    shell_args = questionary.select('choose a shell', Constants.SHELLS, use_shortcuts=True).ask().split('+', 1)
    handle_additional_price_selection(receipt, shell_args, prefix_keys=(Constants.TACO_PARENT_KEY,))

    meat_args = questionary.select('choose your meat', Constants.MEATS, use_shortcuts=True).ask().split('+', 1)
    handle_additional_price_selection(receipt, meat_args, prefix_keys=(Constants.TACO_PARENT_KEY,))

    toppings = questionary.checkbox('choose your toppings', Constants.TOPPINGS, validate=topping_validator).ask()
    for topping in toppings:
        receipt.append(topping, prefix_keys=(Constants.TACO_PARENT_KEY,))

    print('\n\n')
    total = 0
    for item in receipt.iter_items():
        if item.has_price:
            total += item.price
            print(f'{"  " * item.depth}{item.name} {f"(${item.price})" if item.has_price else ""}')
        else:
            print(f'{"  " * item.depth}{item.name}')
    print(f'\nTOTAL: ${total}')


ask_for_taco()
