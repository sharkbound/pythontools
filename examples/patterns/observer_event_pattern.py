from dataclasses import dataclass
from typing import Callable, Optional, Generic, Type, TypeVar

ItemType = TypeVar('ItemType')
EventType = TypeVar('EventType')

ListenerAlias = Callable[[ItemType], None]


class Observer(Generic[ItemType, EventType]):
    def __init__(self):
        self.subscribers: list[ListenerAlias] = []

    def subscribe(self, other: ListenerAlias) -> Callable[[], None]:
        self.subscribers.append(other)
        return lambda: self.subscribers.remove(other)

    def __call__(self, event: EventType):
        for subscriber in self.subscribers:
            subscriber(event)


@dataclass
class Item:
    name: str
    amount: int
    id: str = ''

    def __post_init__(self):
        if not self.id:
            self.id = self.name


class ItemChangedEvent(Generic[ItemType]):
    def __init__(self, type: str, item: ItemType):
        self.type = type
        self.item = item


class ItemDatabase(Generic[ItemType, EventType]):
    def __init__(self):
        self.event: Observer[ItemType, EventType] = Observer()
        self.items: dict[str, ItemType] = {}

    def add(self, item: ItemType):
        if item.name in self.items:
            self.items[item.name].amount += 1
        else:
            self.items[item.name] = item

        self.event(ItemChangedEvent('add', item))

    def remove(self, item: ItemType):
        if item.name not in self.items:
            return

        stored = self.items[item.name]

        if stored.amount < item.amount:
            del self.items[item.name]
            self.event(ItemChangedEvent('delete', item))
            return

        stored.amount -= item.amount
        self.event(ItemChangedEvent('remove', item))

    def listen(self, listener: ListenerAlias[EventType]) -> Callable[[], None]:
        return self.event.subscribe(listener)

    def find_best(self, score_func: Callable[[ItemType], int]) -> Optional[ItemType]:
        if not self.items:
            return None

        return max(self.items.values(), key=score_func)


db: ItemDatabase[Item, ItemChangedEvent] = ItemDatabase()
db.listen(lambda event: print(event.__dict__))
db.add(Item('banana', 100))
db.add(Item('apple', 30))
db.add(Item('grape', 250))
db.add(Item('watermelon', 10))

print(f'best by amount: {db.find_best(lambda x: x.amount)}')
print(f'best by name length: {db.find_best(lambda x: len(x.name))}')
