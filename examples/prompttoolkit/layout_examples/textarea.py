from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

text_in = TextArea('text', height=1, read_only=True)

app = Application(
    layout=Layout(
        HSplit(
            [
                text_in
            ]
        )
    )
)

app.run()
