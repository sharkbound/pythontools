from collections import defaultdict
from typing import Hashable


def _iter_2d_coords(topleft, bottomright, bucket_size):
    for x in range(min(int(topleft[0]), int(bottomright[0])) // bucket_size, (max(int(topleft[0]), int(bottomright[0])) // bucket_size) + 1):
        for y in range(min(int(topleft[1]), int(bottomright[1])) // bucket_size, (max(int(topleft[1]), int(bottomright[1])) // bucket_size) + 1):
            yield x, y


class HashGrid:
    def __init__(self, bucket_size=200):
        self.bucket_size = bucket_size
        self._contents: defaultdict[Hashable, list] = defaultdict(list)
        self._buckets_for_object: defaultdict[Hashable, list] = defaultdict(list)

    def add(self, obj, bounds):
        for x, y in _iter_2d_coords(bounds[0], bounds[1], self.bucket_size):
            bucket = self._contents[x, y]
            bucket.append(obj)
            self._buckets_for_object[obj].append(bucket)

    def add_all(self, *obj_bound_pairs):
        for obj, bound in obj_bound_pairs:
            self.add(obj, bound)

    def remove(self, obj):
        if obj not in self._buckets_for_object:
            return False
        for bucket in self._buckets_for_object[obj]:
            bucket.remove(obj)
        del self._buckets_for_object[obj]

    def update(self, obj, bounds):
        if obj not in self._buckets_for_object:
            return False
        for bucket in self._buckets_for_object[obj]:
            bucket.remove(obj)
        self._buckets_for_object[obj].clear()

        for x, y in _iter_2d_coords(bounds[0], bounds[1], self.bucket_size):
            bucket = self._contents[x, y]
            bucket.append(obj)
            self._buckets_for_object[obj].append(bucket)
        return True

    def to_bucket_coord(self, point):
        return int(point[0] // self.bucket_size), int(point[1] // self.bucket_size)

    def clear_bounds(self, bounds, filter_func=None):
        for x, y in _iter_2d_coords(bounds[0], bounds[1], self.bucket_size):
            if (coords := (x, y)) in self._contents:
                bucket = self._contents[coords]
                if filter_func is None:
                    bucket.clear()
                    del self._contents[coords]
                else:
                    container = bucket
                    for obj in tuple(filter(filter_func, container)):
                        container.remove(obj)
                        self._buckets_for_object[obj].remove(container)
                    if not container:
                        del self._contents[coords]

    def clear_point(self, point, filter_func=None):
        point = self.to_bucket_coord(point)
        if point not in self._contents:
            return

        bucket = self._contents[point]
        if filter_func is None:
            bucket.clear()
            del self._contents[point]
        else:
            container = bucket
            for obj in tuple(filter(filter_func, container)):
                container.remove(obj)
                self._buckets_for_object[obj].remove(container)
            if not container:
                del self._contents[point]

    def clear(self):
        self._contents.clear()
        self._buckets_for_object.clear()

    def get_objects_for_point(self, point):
        point = self.to_bucket_coord(point)
        if point in self._contents:
            return set(self._contents[point])
        return set()

    def get_objects_for_area(self, bounds):
        objects = []
        for point in _iter_2d_coords(bounds[0], bounds[1], self.bucket_size):
            if point in self._contents:
                objects.extend(self._contents[point])
        return set(objects)

    def get_all_objects(self):
        seen = set()
        for bucket in self._contents.values():
            for obj in bucket:
                if obj not in seen:
                    yield obj
                    seen.add(obj)

    def debug(self):
        print('--------------------------------------------------------')
        print(f'{self._contents=}\n\t{len(self._contents)=}')
        print(f'{self._buckets_for_object=}\n\t{len(self._buckets_for_object)=}')
        print('--------------------------------------------------------')
