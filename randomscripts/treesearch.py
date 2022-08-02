from dataclasses import dataclass, field
from typing import Optional

from icecream import ic


@dataclass(frozen=True)
class SearchResult:
    depth: int
    unmatched: str
    matched: str
    node: 'Node' = field(repr=False)
    parent: Optional['Node'] = field(repr=False, default=None)

    @property
    def unmatched_length(self):
        return len(self.unmatched)

    @property
    def matched_length(self):
        return len(self.matched)


@dataclass
class Node:
    children: list = field(default_factory=list)
    values: set = field(default_factory=set)
    depth: int = field(default=0)

    def add_child(self):
        node = Node(depth=self.depth + 1)
        self.children.append(node)
        return node

    def get_child_from_value(self, value, add_if_missing=True):
        node = next(filter(lambda x: x.has_value(value), self.children), None)
        if add_if_missing and node is None:
            return self.add_child()
        return node

    def add_value(self, value):
        self.values.add(value)
        return self

    def has_value(self, value):
        return value in self.values

    def _search(self, string: str, parent: 'Node' = None, matched: str = ''):
        if not string:
            return SearchResult(depth=self.depth, unmatched=string, node=self, parent=parent, matched=matched)

        if child_with_value := self.get_child_from_value(string[0], add_if_missing=False):
            return child_with_value._search(string=string[1:], parent=self, matched=matched + string[0])

        has_value_in_self = self.has_value(string[0])
        if has_value_in_self and len(string) == 1:
            return SearchResult(depth=self.depth, unmatched=string[1:], node=self, parent=parent, matched=matched + string[0])

        elif has_value_in_self and len(string) > 1 and (child_with_value := self.get_child_from_value(string[1], add_if_missing=False)) is not None:
            return child_with_value._search(string=string[1:], parent=self, matched=matched + string[0])

        elif has_value_in_self and len(string) > 1:
            return SearchResult(depth=self.depth, unmatched=string[1:], node=self, parent=parent, matched=matched + string[0])

        return SearchResult(depth=self.depth, unmatched=string, node=self, parent=parent, matched=matched)

    def search(self, string: str) -> SearchResult:
        return self._search(string, None, '')

    def add_chain(self, values):
        """
        recursively adds values to subnodes until it adds them all
        """
        if not values:
            return

        node = self
        for value in values:
            node.add_value(value)
            # TODO: fix wierd overriding issue with this pair, this i suspect is the cause
            #                    v
            node = node.add_child()

    def pretty_print(self):
        if self.values:
            print('  ' * self.depth, ', '.join(self.values), sep='')
        for child in self.children:
            child.pretty_print()

    @property
    def has_children(self):
        return bool(self.children)

    @property
    def has_values(self):
        return bool(self.values)


if __name__ == '__main__':
    nodes = Node()
    # TODO: fix wierd overriding issue with this pair
    #                    v
    for oper in {'<=', '<<'}:  # {'=', '==', '!=', '>', '>=', '<', '<=', '->', '<-',}:
        nodes.add_chain(oper)

    # nodes.pretty_print()
    # print('\n\n\n')
    match = nodes.search('<=')
    ic(
        match,
        match.node
    )
