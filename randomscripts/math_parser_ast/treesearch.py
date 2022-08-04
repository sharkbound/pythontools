from dataclasses import dataclass, field, replace
from typing import Optional, Iterable, TypeVar, Callable, Protocol, Hashable, Sequence, Any

from icecream import ic

TupleOfHashables = tuple[Hashable, ...]
ListOfHashables = list[Hashable, ...]


@dataclass(frozen=True)
class SearchResult:
    matched: TupleOfHashables
    unmatched: TupleOfHashables
    query: TupleOfHashables
    all_matches: ListOfHashables = field(repr=False)

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
            remaining: TupleOfHashables,
            matched: TupleOfHashables,
            all_matches: ListOfHashables,
            query: TupleOfHashables = None
    ) -> SearchResult:
        if not remaining:
            all_matches.append(result := SearchResult(unmatched=remaining, matched=matched, query=query, all_matches=[]))
            return result

        if not self.has_value(remaining[0]):
            return SearchResult(unmatched=remaining, matched=matched, query=query, all_matches=all_matches)

        matched = matched + (remaining[0],)
        remaining = remaining[1:]
        all_matches.append(SearchResult(unmatched=remaining, matched=matched, query=query, all_matches=[]))

        if remaining and (child_with_value := self.get_child_from_value(remaining[0], add_if_missing=False)):
            return child_with_value._search(remaining=remaining, matched=matched, query=query, all_matches=all_matches)

        return SearchResult(unmatched=remaining, matched=matched, query=query, all_matches=all_matches)

    def search(self, query: Iterable[Hashable]) -> SearchResult:
        query = tuple(query)
        return self._search(remaining=query, matched=(), query=query, all_matches=[])

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


def format_search_results(result: SearchResult, formatter: Callable[[tuple[Hashable]], Any]) -> SearchResult:
    return SearchResult(
        unmatched=formatter(result.unmatched),
        matched=formatter(result.matched),
        query=formatter(result.query),
        all_matches=[format_search_results(x, formatter) for x in result.all_matches]
    )


# noinspection PyTypeChecker
def format_search_results_all(results: Iterable[SearchResult], formatter: Callable[[tuple[Hashable]], Any]) -> SearchResult:
    return [format_search_results(result, formatter) for result in results]


def search_filter_true(query: Iterable[Hashable], filter: Callable[[SearchResult], bool], nodes: Node) -> list[SearchResult]:
    result = nodes.search(query)
    return [r for r in result.all_matches if filter(r)]


def search_filter_true_first(query: Iterable[Hashable], predicate: Callable[[SearchResult], bool], nodes: Node) -> Optional[SearchResult]:
    return next(filter(predicate, nodes.search(query).all_matches), None)


def search_filter_true_last(query: Iterable[Hashable], predicate: Callable[[SearchResult], bool], nodes: Node) -> Optional[SearchResult]:
    result = nodes.search(query)
    value = None
    for match in result.all_matches:
        if predicate(match):
            value = match
    return value


def search_filter_false(query: Iterable[Hashable], filter: Callable[[SearchResult], bool], nodes: Node) -> list[SearchResult]:
    return [r for r in nodes.search(query).all_matches if not filter(r)]


def search_filter_false_first(query: Iterable[Hashable], predicate: Callable[[SearchResult], bool], nodes: Node) -> Optional[SearchResult]:
    result = nodes.search(query)
    return next(filter(lambda x: not predicate(x), result.all_matches), None)


def search_filter_false_last(query: Iterable[Hashable], predicate: Callable[[SearchResult], bool], nodes: Node) -> Optional[SearchResult]:
    result = nodes.search(query)
    value = None
    for match in result.all_matches:
        if not predicate(match):
            value = match
    return value


if __name__ == '__main__':
    nodes = Node().add_from_iterables({'12545'} | set('*/-+^') | {'=', '==', '!=', '<', '>', '<=', '>='} | {'*', '/', '-', '+', '^'})
    nodes.pretty_print()
    ic(format_search_results_all(nodes.search('12545').all_matches, ''.join))
