import asyncio
from typing import Iterable, AsyncGenerator

from prompt_toolkit import completion, styles, PromptSession
from prompt_toolkit.completion import CompleteEvent, Completion, WordCompleter
from prompt_toolkit.document import Document


class AdventureCompleter(completion.Completer):
    _attack_target_completer = WordCompleter(['guaroth', 'jokura', 'illiy'])
    _actions_completer = WordCompleter(['attack', 'roll', 'dance', 'open', 'search'])

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        pass

    async def get_completions_async(self, document: Document, complete_event: CompleteEvent) -> AsyncGenerator[Completion, None]:
        prior_text = document.text_before_cursor
        parts = prior_text.strip().split()
        word_index = len(parts) - 1

        if word_index < 0 or prior_text[-1].isspace():
            word_index = max(word_index + 1, 0)

        if word_index == 0 or not parts:
            completer = self._actions_completer
        elif word_index == 1:
            completer = self._attack_target_completer
        else:
            completer = None

        if completer is not None:
            async for completion in completer.get_completions_async(document, complete_event):
                yield completion


async def main():
    prompt_session = PromptSession(
        message='> ',
        completer=AdventureCompleter(),
        bottom_toolbar=[('class:bottom-toolbar', 'start typing to get completions!')],
        style=styles.Style.from_dict({
            'bottom-toolbar': 'fg:#6c82ff bg:#d83def'
        }),
        erase_when_done=True
    )
    while True:
        print(await prompt_session.prompt_async())


asyncio.run(main())
