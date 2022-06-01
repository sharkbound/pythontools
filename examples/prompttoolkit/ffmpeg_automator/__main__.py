import os
from pathlib import Path

import prompt_toolkit as ptt
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
import questionary


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


class FileSelectors:
    def __init__(self):
        self.key_bindings = ptt.key_binding.KeyBindings()
        self.key_bindings.add(Keys.Any, eager=True)(self.on_key_press)
        self.key_bindings.add(Keys.ControlC, eager=True)(lambda _: self.app.exit())
        self.key_bindings.add(Keys.Up, eager=True)(self.on_up_pressed)
        self.key_bindings.add(Keys.Down, eager=True)(self.on_down_pressed)
        self.key_bindings.add(Keys.Enter, eager=True)(self.on_enter_pressed)
        self.styles = Style([
            ('filter', 'bg:#000000 fg:#ffff00'),
            ('selected', 'fg:#ff0000')
        ])
        self.session, self.app = create_app(self.key_bindings, self.styles, self.tokens)
        self.path = Path(os.getcwd())
        self._dir_items = list(self.path.glob('*'))
        self._filter = ''
        self._index = IndexSelector(self._dir_items)

    def on_key_press(self, keys: KeyPressEvent):
        key = keys.key_sequence[0]
        if key.key is Keys.ControlH:
            self._filter = self._filter[:-1]
            return
        self._filter += key.data

    def on_up_pressed(self, key):
        self._index.up()

    def on_down_pressed(self, key):
        self._index.down()

    def on_enter_pressed(self, key):
        if self.path.is_dir():
            self.path = self._index.current_item
            self._dir_items = list(self.path.glob('*'))
            self._index.items = self._dir_items
            self._index.index = 0
        elif self.path.is_file():
            # todo, blackout issue, erase previous items
            print(f'FOUND: {self.path}')

    def tokens(self):
        return [('class:filter', f'{self._filter}\n')] + [
            (
                'class:selected' if index == self._index.index else '',
                f'{"[DIR ]" if path.is_dir() else "[FILE]"} - {path.name}\n'
            )
            for index, path in enumerate(self._dir_items)
            if not self._filter or self._filter in path.name
        ]

    def start(self):
        _fix_unecessary_blank_lines(self.session)
        self.app.run()


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
    # disables the cursor, it is not used actively on the quiz example
    ps.layout.current_window.always_hide_cursor = Always()


FileSelectors().start()
