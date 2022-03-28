from functools import lru_cache

import numpy as np


class Vector(np.ndarray):
    @staticmethod
    @lru_cache(maxsize=100)
    def __new__(cls, x: float, y: float) -> 'Vector':
        arr: Vector = np.asarray([x, y], dtype=np.float64).view(cls)
        arr.setflags(write=False)
        return arr

    def tuplef(self):
        return tuple(self)

    def tuple(self):
        return self.x, self.y

    def move_rel(self, x=0, y=0) -> 'Vector':
        return self + (x, y)

    def is_zero(self, tolerance=.01):
        return abs(self[0]) <= tolerance and abs(self[1]) <= tolerance

    def is_near(self, other: 'Vector', tolerance=.01):
        return abs(other.xf - self.xf) <= tolerance and abs(other.yf - self.yf) <= tolerance

    def abs_diff(self, other: 'Vector'):
        return abs(other.xf - self.xf) + abs(other.yf - self.yf)

    def abs_diff_tuple(self, other: 'Vector'):
        return Vector(abs(other.xf - self.xf), abs(other.yf - self.yf))

    def copy(self, x=None, y=None):
        return Vector(self.x if x is None else x, self.y if y is None else y)

    @property
    def x(self):
        return int(self[0])

    @property
    def y(self):
        return int(self[1])

    @property
    def xf(self):
        return self[0]

    @property
    def yf(self):
        return self[1]

    @property
    def length(self):
        return (self.xf ** 2 + self.yf ** 2) ** .5

    @property
    def normalized(self):
        length = self.length
        return Vector(self.xf / length, self.yf / length)

    def __iadd__(self, other) -> 'Vector':
        return super().__add__(other)

    def __isub__(self, other) -> 'Vector':
        return super().__sub__(other)

    def __itruediv__(self, other) -> 'Vector':
        return super().__truediv__(other)

    def __ifloordiv__(self, other) -> 'Vector':
        return super().__floordiv__(other)

    def __imul__(self, other) -> 'Vector':
        return super().__mul__(other)

    def __imod__(self, other) -> 'Vector':
        return super().__mod__(other)

    def __hash__(self):
        return hash(self.tuple())

    def __eq__(self, other):
        return np.array_equal(self, other)
