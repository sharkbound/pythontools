from dataclasses import dataclass, field
from typing import Optional

from icecream import ic


@dataclass(frozen=True)
class SearchResult:
    depth: int
    unmatched: str
    matched: str
    parent: Optional['Node'] = field(repr=False, default=None)

    @property
    def unmatched_length(self):
        return len(self.unmatched)

    @property
    def is_full_match(self):
        return not bool(self.unmatched)

    @property
    def matched_length(self):
        return len(self.matched)


_ids = iter(range(10000))


@dataclass
class Node:
    children: list = field(default_factory=list)
    values: set = field(default_factory=set)
    depth: int = field(default=0)
    _id: int = field(default_factory=lambda: next(_ids))

    def add_child(self):
        node = Node(depth=self.depth + 1)
        self.children.append(node)
        return node

    def get_child_from_value(self, value, add_if_missing=False):
        node = next(filter(lambda x: x.has_value(value), self.children), None)
        if add_if_missing and node is None:
            return self.add_child()
        return node

    def add_value(self, value):
        self.values.add(value)
        return self

    def has_value(self, value):
        return value in self.values

    def _search(self, string: str, parent: 'Node' = None, matched: str = '') -> SearchResult:
        if not string or not self.has_value(string[0]):
            return SearchResult(depth=self.depth, unmatched=string, parent=parent, matched=matched)

        matched += string[0]
        string = string[1:]

        if string and (child_with_value := self.get_child_from_value(string[0], add_if_missing=False)):
            return child_with_value._search(string=string, parent=self, matched=matched)

        return SearchResult(depth=self.depth, unmatched=string, matched=matched)

    def search(self, string: str) -> SearchResult:
        return self._search(string, None, '')

    def add_from_iterables(self, iterables):
        for iterable in iterables:
            self.add_from_iterable(iterable)
        return self

    def add_from_iterable(self, values):
        """
        recursively adds values to subnodes until it adds them all
        """
        if not values:
            return

        node = self
        for a, b in zip(values[:-1], values[1:]):
            node.add_value(a)
            node = node.get_child_from_value(b, add_if_missing=True)
            node.add_value(b)
        return self

    def pretty_print(self):
        if self.values:
            print('-' * self.depth, f'ID({self._id}): ', ', '.join(self.values), sep='')
        for child in self.children:
            child.pretty_print()

    @property
    def has_children(self):
        return bool(self.children)

    @property
    def has_values(self):
        return bool(self.values)


if __name__ == '__main__':
    nodes = Node().add_from_iterables(['1234', '124', '134'])
    nodes.pretty_print()
    ic(nodes.search('1'))
    ic(nodes.search('12'))
    ic(nodes.search('123'))
    ic(nodes.search('1234'))
    ic(nodes.search('12345'))
    ic(nodes.search('1345'))
