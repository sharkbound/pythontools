from prompt_toolkit import PromptSession, completion, styles

session = PromptSession(
    completer=completion.WordCompleter(
        words=[
            'roll', 'poke', 'jam', 'add', 'jab'
        ]
    ),
    bottom_toolbar=[('class:bottom-toolbar', 'footer text here')],
    style=styles.Style.from_dict({
        'bottom-toolbar': 'bg:#ff0000 fg:#00ff00'
    })
)

session.prompt('> ')
