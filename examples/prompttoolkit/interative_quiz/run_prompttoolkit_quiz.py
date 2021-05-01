from prompt_toolkit import PromptSession, Application
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.styles import Style


class OptionsTextProvider:
    def __init__(self, *choices):
        self.choices = choices
        self._current_selection = 0
        self.answered = False

    def select(self, index):
        self._current_selection = index % len(self.choices)

    @property
    def current_item(self):
        return self.choices[self._current_selection]

    def up(self):
        self.select(self._current_selection - 1)

    def down(self):
        self.select(self._current_selection + 1)

    def _token_for_index(self, index, value):
        if index == self._current_selection:
            return 'class:quiz_item_selected', f'* > {value}\n'
        return 'class:quiz_item_not_selected', f'{value}\n'

    def tokens(self):
        if self.answered:
            return [('class:quiz_item_selected', f'YOU CHOOSE: "{self.current_item}"')]

        return [
            self._token_for_index(i, v)
            for i, v in enumerate(self.choices)
        ]


class Quiz:
    FG = '#ff0000'
    BG = '#00ff00'

    def __init__(self, text_provider: OptionsTextProvider):
        self.text_provider = text_provider
        self.keybindings = KeyBindings()
        self.style = Style([
            ('quiz_item_selected', f'bg:{self.BG} fg:{self.FG}'),
            ('quiz_item_not_selected', f'bg:{self.FG} fg:{self.BG}')
        ])

        self.keybindings.add(Keys.Up, eager=True)(lambda _: self.text_provider.up())
        self.keybindings.add(Keys.Down, eager=True)(lambda _: self.text_provider.down())
        self.keybindings.add(Keys.Enter, eager=True)(self.enter)
        self.keybindings.add(Keys.Any, eager=True)(lambda _: None)

    def enter(self, e):
        self.text_provider.answered = True
        e.app.exit(result=self.text_provider.current_item)


quiz = Quiz(OptionsTextProvider('a', 'b', 'c'))
session = PromptSession(message=quiz.text_provider.tokens)
app = Application(layout=session.layout, key_bindings=quiz.keybindings, style=quiz.style)
print(f'RESULT: {app.run()}')
