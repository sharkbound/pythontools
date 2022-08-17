import os
from pathlib import Path
from typing import Optional, Callable, Union

import prompt_toolkit as ptt
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style


class IndexSelector:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def up(self):
        self.index = max(self.index - 1, 0)

    def down(self):
        self.index = min(self.index + 1, len(self.items) - 1)

    @property
    def current_item(self):
        return self.items[self.index]

    def update_items(self, items):
        self.index = 0
        self.items = items


def get_page(items, page, items_per_page):
    return items[page * items_per_page: (page + 1) * items_per_page]


def get_page_count(items, items_per_page):
    return int(len(items) / items_per_page) + 1


class FileSelector:
    NOT_SET = object()

    def __init__(self, selection_validator: Callable[[Path], bool] = lambda _: True, initial_path: Path = None):
        self.selection_validator = selection_validator # todo: add support for returning an string, then printing it as a error
        self.key_bindings = ptt.key_binding.KeyBindings()
        self.key_bindings.add(Keys.Any, eager=True)(self.on_key_press)
        self.key_bindings.add(Keys.ControlC, eager=True)(lambda _: self._exit_app())
        self.key_bindings.add(Keys.ControlQ, eager=True)(lambda _: self._exit_app())
        self.key_bindings.add(Keys.Up, eager=True)(self.on_up_pressed)
        self.key_bindings.add(Keys.Down, eager=True)(self.on_down_pressed)
        self.key_bindings.add(Keys.Left, eager=True)(self.on_left_pressed)
        self.key_bindings.add(Keys.Right, eager=True)(self.on_right_pressed)
        self.key_bindings.add(Keys.Enter, eager=True)(self.on_enter_pressed)
        self.key_bindings.add('[', eager=True)(self.on_left_bracket_pressed)
        self.key_bindings.add(']', eager=True)(self.on_right_bracket_pressed)
        self.styles = Style([
            ('filter', 'bg:#000000 fg:#ffff00'),
            ('selected', 'fg:#ff0000'),
            ('nofiles', 'fg:#0000ff'),
            ('final', 'fg:#ffff00'),
            ('pageinfo', 'fg:#ff00ff'),
            ('final_terminated', 'fg:#ff0000'),
        ])
        self.session, self.app = create_app(self.key_bindings, self.styles, self.tokens)
        self.path = initial_path or Path(os.getcwd())
        self._dir_items = list(self.path.glob('*'))
        self._displayed_dir_items = self._dir_items
        self._filter = ''
        self._index = IndexSelector(self._dir_items)
        self._result: Union[object, Optional[Path]] = self.__class__.NOT_SET
        self._current_page = 0
        self._items_per_page = 15
        self._page_count = get_page_count(self._dir_items, self._items_per_page)

    def _exit_app(self):
        self._result = None
        self.app.exit(result=None)

    def update_page(self, page=None, change=None):
        pass

    def _update_path(self, new_path):
        self.path = new_path

    def _update_items_using_current_path(self, reset_filter=False, update_files=False):
        if reset_filter:
            self._filter = ''

        if update_files:
            self._dir_items = list(self.path.glob('*'))
            self._current_page = 0
            self._page_count = get_page_count(self._dir_items, self._items_per_page)

        self._displayed_dir_items = get_page([
            path
            for path in self._dir_items
            if not self._filter or self._filter in path.name.casefold()
        ], self._current_page, self._items_per_page)
        self._index.update_items(self._displayed_dir_items)

    def on_key_press(self, keys: KeyPressEvent):
        key = keys.key_sequence[0]
        if key.key is Keys.ControlH:
            self._filter = self._filter[:-1]
            self._update_items_using_current_path()
            return
        self._filter += key.data.casefold()
        self._update_items_using_current_path()

    @property
    def selected_item(self):
        return self._index.current_item

    def on_up_pressed(self, _):
        self._index.up()

    def on_down_pressed(self, _):
        self._index.down()

    def on_left_pressed(self, _):
        self._update_path(self.path.parent)
        self._update_items_using_current_path(reset_filter=True, update_files=True)

    def on_right_pressed(self, _):
        if self.selected_item.is_dir():
            self._update_path(self.selected_item)
            self._update_items_using_current_path(reset_filter=True, update_files=True)

    def on_enter_pressed(self, _):
        if self._index.items and self.selection_validator(self.selected_item):
            self._result = self.selected_item
            self.app.exit(result=self.selected_item)

    def on_left_bracket_pressed(self, _):
        self._current_page = max(self._current_page - 1, 0)
        self._update_items_using_current_path()

    def on_right_bracket_pressed(self, _):
        self._current_page = min(self._current_page + 1, self._page_count - 1)
        self._update_items_using_current_path()

    def tokens(self):
        if self._result is not self.__class__.NOT_SET:
            if self._result is None:
                return [('class:final_terminated', 'Dialog cancelled by user input (CTRL+C) OR (CTRL+Q)')]
            return [('class:final', f'selected path: {self._result}')]

        ret = [
            ('', 'CONTROLS: \nLEFT ARROW = BACK A DIRECTORY'
                 ' / RIGHT ARROW = EXPAND THE SELECTED'
                 ' / UP ARROW = MOVE UP'
                 ' / DOWN ARROW = MOVE DOWN\n\n'
             ),
            ('class:filter', f'[FILTER: {self._filter if self._filter else "[NO FILTER, TYPE TO APPLY FILTER]"}]\n'),
            ('', f'[PATH: {self.path}]\n\n'),
        ]

        if self._displayed_dir_items:
            ret.extend(
                (
                    'class:selected' if index == self._index.index else '',
                    f'{"[DIR ]" if path.is_dir() else "[FILE]"} - {path.name}\n'
                )
                for index, path in enumerate(self._displayed_dir_items)
                if not self._filter or self._filter in path.name.casefold()
            )
            ret.append((
                'class:pageinfo',
                f'\n\nPAGE [{self._current_page + 1} / {self._page_count}]\n( [ ) to go back a page, ( ] ) to go forward a page'
            ))
        else:
            ret.append(('class:nofiles', '[NO FILES FOUND FOR CURRENT PATH]'))
        return ret

    def start(self):
        _fix_unnecessary_blank_lines(self.session)
        return self.app.run()


def create_app(key_bindings, styles, token_func):
    return (
        session := ptt.PromptSession(message=token_func),
        ptt.Application(layout=session.layout, key_bindings=key_bindings, style=styles)
    )


# from questionary on pypi, i shorted it from the original
def _fix_unnecessary_blank_lines(ps: ptt.PromptSession) -> None:
    """This is a fix for additional empty lines added by prompt toolkit.

    This assumes the layout of the default session doesn't change, if it
    does, this needs an update."""
    from prompt_toolkit.filters import Always
    # this forces the main window to stay as small as possible, avoiding empty lines in selections
    ps.layout.current_window.dont_extend_height = Always()
    # disables the cursor
    ps.layout.current_window.always_hide_cursor = Always()
