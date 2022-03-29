import dataclasses
import random
import uuid
from collections import namedtuple

import numpy as np
import arcade as arc

from typing import Callable
from misc.hashgrid import HashGrid
from shapely import geometry as geo
from misc.vector import Vector

WIN_WIDTH = 800
WIN_HEIGHT = 600
ANT_COUNT = 5000


class BoxBounds:
    __slots__ = ('box', 'min_x', 'min_y', 'max_x', 'max_y', 'uuid')

    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.box = geo.box(min_x, min_y, max_x, max_y)
        self.uuid = uuid.uuid4()

    @property
    def bottom_left(self):
        return Vector(self.min_x, self.min_y)

    @property
    def top_left(self):
        return Vector(self.min_x, self.max_y)

    @property
    def bottom_right(self):
        return Vector(self.max_x, self.min_y)

    @property
    def top_right(self):
        return Vector(self.max_x, self.max_y)

    @property
    def center(self):
        return Vector((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)

    @property
    def size(self):
        return Vector(self.max_x - self.min_x, self.max_y - self.min_y)

    def __contains__(self, item):
        match item:
            case Vector():
                return self.box.intersects(geo.Point(item.x, item.y))
            case BoxBounds() | geo.Polygon() | geo.Point():
                return self.box.intersects(item)
            case _:
                raise ValueError(f'invalid type for __contains__ in {self.__class__.__name__}: {type(item)}')

    def __hash__(self):
        return hash((int(self.min_x), int(self.max_x), int(self.min_y), int(self.max_y), self.uuid))


def create_box(v1, v2):
    return BoxBounds(
        min(v1.x, v2.x),
        min(v1.y, v2.y),
        max(v1.x, v2.x),
        max(v1.y, v2.y)
    )


def create_box_args(x1, y1, x2, y2):
    return BoxBounds(
        min(x1, x2),
        min(y1, y2),
        max(x1, x2),
        max(y1, y2)
    )


class Ant(namedtuple('Ant', 'id pos size color velocity')):
    @property
    def bounds(self):
        return create_box_args(
            self.pos[0] - self.size / 2,
            self.pos[1] - self.size / 2,
            self.pos[0] + self.size / 2,
            self.pos[1] + self.size / 2
        )


class View(arc.View):
    def __init__(self):
        super().__init__()
        arc.set_background_color((0, 0, 0))
        self.grid = HashGrid(10)
        self.ants = {
            id: Ant(
                id=id,
                pos=np.array([rx, ry]),
                size=random.randint(1, 10),
                color=np.random.default_rng().integers(0, 255, 3),
                velocity=np.random.default_rng().uniform(-150, 150, 2),
            )

            for id, (rx, ry) in enumerate(zip(
                np.random.default_rng().uniform(0, WIN_WIDTH, ANT_COUNT),
                np.random.default_rng().uniform(0, WIN_HEIGHT, ANT_COUNT)
            ))
        }
        for ant in self.ants.values():
            self.grid.add(ant.id, (ant.bounds.bottom_left, ant.bounds.top_right))

    @property
    def mouse(self):
        return Vector(self.window._mouse_x, self.window._mouse_y)

    def on_update(self, delta_time: float):
        # self.grid.clear()
        #
        # for ant in self.ants.values():
        #     if (ant.pos[0] < 0 and ant.velocity[0] < 0) or (ant.pos[0] > WIN_WIDTH - 1 and ant.velocity[0] > 0):
        #         ant.velocity[0] *= -1
        #     if (ant.pos[1] < 0 and ant.velocity[1] < 0) or (ant.pos[1] > WIN_HEIGHT - 1 and ant.velocity[1] > 0):
        #         ant.velocity[1] *= -1
        #
        #     ant.pos[0] += ant.velocity[0] * delta_time
        #     ant.pos[1] += ant.velocity[1] * delta_time
        #
        #     self.grid.add(ant.id, (ant.bounds.bottom_left, ant.bounds.top_right))

        self.window.set_caption(str(1 / delta_time))

    def on_draw(self):
        arc.start_render()
        mouse = self.mouse

        # for ant in self.ants.values():
        #     arc.draw_circle_filled(*ant.pos, ant.size, (*ant.color, 50))
        RADIUS = 200
        arc.draw_rectangle_outline(mouse.x, mouse.y, RADIUS, RADIUS, arc.color.TEAL)
        mouse_bounds = create_box(mouse - RADIUS / 2, mouse + RADIUS / 2)
        for ant in map(self.ants.get, self.grid.get_objects_for_area((mouse_bounds.bottom_left, mouse_bounds.top_right))):
            # if ant.bounds.box in mouse_bounds:
            arc.draw_circle_filled(*ant.pos, ant.size, ant.color)
        print(len(self.grid._contents))


win = arc.Window(width=WIN_WIDTH, height=WIN_HEIGHT)
win.show_view(View())
win.run()
