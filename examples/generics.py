from typing import Generic, TypeVar, Generator

T = TypeVar('T')


class ItemCollection(Generic[T]):
    def __init__(self, *items: T):
        self.items = items
        self.it = iter(items)

    def next(self) -> T:
        return next(self.it)

    def __iter__(self) -> Generator[T, None, None]:
        yield from self.items


items = ItemCollection('1')
for item in items:
    print(item.__len__())
