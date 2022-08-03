from dataclasses import dataclass, field
from typing import Optional, Sequence, Iterable, TypeVar, Generic

from icecream import ic

T = TypeVar('T')


@dataclass(frozen=True)
class SearchResult(Generic[T]):
    depth: int
    unmatched: Sequence[T]
    matched: Sequence[T]
    query: Sequence[T]
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
class Node(Generic[T]):
    children: list['Node'] = field(default_factory=list)
    values: set[T] = field(default_factory=set)
    depth: int = field(default=0)
    _id: int = field(default_factory=lambda: next(_ids))

    def add_child(self):
        node = Node(depth=self.depth + 1)
        self.children.append(node)
        return node

    def get_child_from_value(self, value: T, add_if_missing=False) -> Optional['Node']:
        node = next(filter(lambda x: x.has_value(value), self.children), None)
        if add_if_missing and node is None:
            return self.add_child()
        return node

    def add_value(self, value: T):
        self.values.add(value)
        return self

    def has_value(self, value: T):
        return value in self.values

    def has_child_with_value(self, value: T):
        return self.children and any(child.has_value(value) for child in self.children)

    def _search(self, string: Sequence[T], parent: 'Node' = None, matched: Sequence = '', query: Sequence = None) -> SearchResult:
        if not string or not self.has_value(string[0]):
            return SearchResult(depth=self.depth, unmatched=string, parent=parent, matched=matched, query=query)

        matched += string[0]
        string = string[1:]

        if string and (child_with_value := self.get_child_from_value(string[0], add_if_missing=False)):
            return child_with_value._search(string=string, parent=self, matched=matched, query=query)

        return SearchResult(depth=self.depth, unmatched=string, matched=matched, query=query)

    def search(self, query: Sequence[T]) -> SearchResult:
        return self._search(string=query, parent=None, matched='', query=query)

    def add_from_iterables(self, iterables: Iterable[Sequence[T]]):
        for iterable in iterables:
            self.add_from_iterable(iterable)
        return self

    def add_from_iterable(self, values: Sequence[T]):
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
    ic(nodes.search('*='))
