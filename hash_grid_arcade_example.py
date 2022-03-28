import dataclasses
from typing import Callable
from misc.hashgrid import HashGrid
import arcade as arc
from shapely import geometry as geo
from misc.vector import Vector


class BoxBounds:
    __slots__ = ('box', 'min_x', 'min_y', 'max_x', 'max_y')

    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.box = geo.box(min_x, min_y, max_x, max_y)

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
        return hash((int(self.min_x), int(self.max_x), int(self.min_y), int(self.max_y)))


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


def render_bounds(bb: BoxBounds, color, thickness=1):
    arc.draw_rectangle_outline(bb.center.x, bb.center.y, bb.size.x, bb.size.y, color, border_width=thickness)


@dataclasses.dataclass(unsafe_hash=True)
class Interactable:
    id: str = dataclasses.field(hash=True)
    bounds: BoxBounds = dataclasses.field(hash=True)
    render: Callable = None

    @property
    def bounds_tuple(self):
        return self.bounds.bottom_left, self.bounds.top_right

    def __repr__(self):
        return f'<{type(self).__name__} id={self.id}>'


class View(arc.View):
    def __init__(self):
        super().__init__()
        arc.set_background_color((0, 0, 0))
        self.grid = HashGrid(100)
        self.interactables: list[Interactable] = [
            Interactable('0', create_box_args(100, 100, 200, 200)),
            Interactable('1', create_box_args(300, 400, 500, 700)),
            Interactable('2', create_box_args(400, 600, 0, 100)),
            Interactable('3', create_box_args(200, 800, 400, 300)),
            Interactable('3', create_box_args(300, 400, 600, 0)),
        ]
        for interactable in self.interactables:
            self.grid.add(interactable, interactable.bounds_tuple)

    @property
    def mouse(self):
        return Vector(self.window._mouse_x, self.window._mouse_y)

    def on_draw(self):
        arc.start_render()
        for obj in self.interactables:
            render_bounds(obj.bounds, (155, 155, 0, 100))
            arc.draw_point(obj.bounds.center.x, obj.bounds.center.y, (255, 0, 0), 10)
        for interactable in filter(lambda x: self.mouse in x.bounds, self.grid.get_objects_for_point(self.mouse)):
            box = interactable.bounds
            arc.draw_point(box.center.xf, box.center.yf, (255, 0, 0), 10)
            render_bounds(box, (255, 255, 0), 5)


win = arc.Window(width=800, height=600)
win.show_view(View())
win.run()
