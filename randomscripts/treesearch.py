from dataclasses import dataclass, field
from typing import Optional, Iterable, TypeVar, Callable, Protocol, Hashable, Sequence

from icecream import ic

TupleOfHashables = tuple[Hashable, ...]


@dataclass(frozen=True)
class SearchResult:
    unmatched: TupleOfHashables
    matched: TupleOfHashables
    query: TupleOfHashables

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
    children: list['Node'] = field(default_factory=list)
    values: set[Hashable] = field(default_factory=set)
    depth: int = field(default=0)
    _id: int = field(default_factory=lambda: next(_ids))

    def add_child(self):
        node = Node(depth=self.depth + 1)
        self.children.append(node)
        return node

    def get_child_from_value(self, value: Hashable, add_if_missing=False) -> Optional['Node']:
        node = next(filter(lambda x: x.has_value(value), self.children), None)
        if add_if_missing and node is None:
            return self.add_child()
        return node

    def add_value(self, value: Hashable):
        self.values.add(value)
        return self

    def has_value(self, value: Hashable):
        return value in self.values

    def has_child_with_value(self, value: Hashable):
        return self.children and any(child.has_value(value) for child in self.children)

    def _search(
            self,
            string: TupleOfHashables,
            matched: TupleOfHashables,
            query: TupleOfHashables = None
    ) -> SearchResult:
        if not string or not self.has_value(string[0]):
            return SearchResult(unmatched=string, matched=matched, query=query)

        matched = matched + (string[0],)
        string = string[1:]

        if string and (child_with_value := self.get_child_from_value(string[0], add_if_missing=False)):
            return child_with_value._search(string=string, matched=matched, query=query)

        return SearchResult(unmatched=string, matched=matched, query=query)

    def search(self, query: Iterable[Hashable]) -> SearchResult:
        query = tuple(query)
        return self._search(string=query, matched=(), query=query)

    def add_from_iterables(self, iterables: Iterable[Sequence[TupleOfHashables]]):
        for iterable in iterables:
            self.add_from_iterable(iterable)
        return self

    def add_from_iterable(self, values: Sequence[Hashable]):
        """
        recursively adds values to subnodes until it adds them all
        """
        if not values:
            return self

        if len(values) == 1:
            self.add_value(values[0])
            return self

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
    nodes = Node().add_from_iterables(set('*/-+^') | {'=', '==', '!=', '<', '>', '<=', '>='} | {'*', '/', '-', '+', '^'})
    nodes.pretty_print()
    ic(nodes.search(['-', '+']))
