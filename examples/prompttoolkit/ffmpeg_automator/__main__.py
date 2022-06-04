import os
from pathlib import Path
from typing import Optional, Callable

import prompt_toolkit as ptt
from icecream import ic
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style

import logging

# LOGGER = logging.getLogger('filelogger')
logging.basicConfig(filename='logging.log')


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


class FileSelectors:
    def __init__(self, selection_validator: Callable[[Path], bool] = lambda _: True):
        self.selection_validator = selection_validator
        self.key_bindings = ptt.key_binding.KeyBindings()
        self.key_bindings.add(Keys.Any, eager=True)(self.on_key_press)
        self.key_bindings.add(Keys.ControlC, eager=True)(lambda _: self.app.exit())
        self.key_bindings.add(Keys.Up, eager=True)(self.on_up_pressed)
        self.key_bindings.add(Keys.Down, eager=True)(self.on_down_pressed)
        self.key_bindings.add(Keys.Left, eager=True)(self.on_left_pressed)
        self.key_bindings.add(Keys.Right, eager=True)(self.on_right_pressed)
        self.key_bindings.add(Keys.Enter, eager=True)(self.on_enter_pressed)
        self.styles = Style([
            ('filter', 'bg:#000000 fg:#ffff00'),
            ('selected', 'fg:#ff0000'),
            ('nofiles', 'fg:#0000ff'),
        ])
        self.session, self.app = create_app(self.key_bindings, self.styles, self.tokens)
        self.path = Path(os.getcwd())
        self._dir_items = list(self.path.glob('*'))
        self._filter = ''
        self._index = IndexSelector(self._dir_items)
        self._prev_path = self.path
        self._result: Optional[Path] = None

    def _update_path(self, new_path):
        self._prev_path = self.path
        self.path = new_path

    def _update_items_using_current_path(self, reset_filter=False, use_cached_files=False):
        if reset_filter:
            self._filter = ''

        logging.error(f'{self.path} / {self._prev_path} / {self.path == self._prev_path}')
        self._dir_items = [
            path
            for path in (self._dir_items if use_cached_files else self.path.glob('*'))
            if not self._filter or self._filter in path.name.casefold()
        ]
        self._index.update_items(self._dir_items)

    def on_key_press(self, keys: KeyPressEvent):
        key = keys.key_sequence[0]
        if key.key is Keys.ControlH:
            self._filter = self._filter[:-1]
            self._update_items_using_current_path(use_cached_files=True)
            return
        self._filter += key.data.casefold()
        self._update_items_using_current_path(use_cached_files=True)

    @property
    def selected_item(self):
        return self._index.current_item

    def on_up_pressed(self, _):
        self._index.up()

    def on_down_pressed(self, _):
        self._index.down()

    def on_left_pressed(self, _):
        self._update_path(self.path.parent)
        self._update_items_using_current_path(reset_filter=True)

    def on_right_pressed(self, _):
        if self.selected_item.is_dir():
            self._update_path(self.selected_item)
            self._update_items_using_current_path(reset_filter=True)

    def on_enter_pressed(self, _):
        if self.selection_validator(self.selected_item):
            self.app.exit(result=self.selected_item)

    def tokens(self):
        ret = [
            ('', 'CONTROLS: \nLEFT ARROW = BACK A DIRECTORY'
                 ' / RIGHT ARROW = EXPAND THE SELECTED'
                 ' / UP ARROW = MOVE UP'
                 ' / DOWN ARROW = MOVE DOWN\n\n'
             ),
            ('class:filter', f'{self._filter if self._filter else "[NO FILTER: TYPE TO APPLY FILTER]"}\n\n'),
            ('', f'[PATH: {self.path}]\n\n'),

        ]

        if self._dir_items:
            ret.extend(
                (
                    'class:selected' if index == self._index.index else '',
                    f'{"[DIR ]" if path.is_dir() else "[FILE]"} - {path.name}\n'
                )
                for index, path in enumerate(self._dir_items)
                if not self._filter or self._filter in path.name.casefold()
            )
        else:
            ret.append(('class:nofiles', '[NO FILES FOUND FOR CURRENT PATH]'))
        return ret

    def start(self):
        _fix_unecessary_blank_lines(self.session)
        return self.app.run()


def create_app(key_bindings, styles, token_func):
    return (
        session := ptt.PromptSession(message=token_func),
        ptt.Application(layout=session.layout, key_bindings=key_bindings, style=styles)
    )


# from questionary on pypi, i shorted it from the original
def _fix_unecessary_blank_lines(ps: ptt.PromptSession) -> None:
    """This is a fix for additional empty lines added by prompt toolkit.

    This assumes the layout of the default session doesn't change, if it
    does, this needs an update."""
    from prompt_toolkit.filters import Always
    # this forces the main window to stay as small as possible, avoiding empty lines in selections
    ps.layout.current_window.dont_extend_height = Always()
    # disables the cursor
    ps.layout.current_window.always_hide_cursor = Always()


FileSelectors(selection_validator=lambda p: p.suffix == '.mp4').start()
