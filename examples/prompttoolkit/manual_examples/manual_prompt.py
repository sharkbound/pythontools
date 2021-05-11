import itertools
import sys
import time

from prompt_toolkit.input import create_input
from prompt_toolkit.output import create_output
from prompt_toolkit.keys import Keys

output = create_output(sys.stdout)
input_ = create_input(sys.stdin)

options = {
    1: '1) A',
    2: '2) B',
    3: '3) C',
}

chosen = 1


def on_key(key):
    global chosen
    if key.key is Keys.Up:
        chosen -= 1
        chosen = max(1, min(len(options), chosen))
    elif key.key is Keys.Down:
        chosen += 1
        chosen = max(1, min(len(options), chosen))


def format_text():
    for key, option in options.items():
        yield f'> {option}' if key == chosen else f'{option}'


def redraw():
    output.cursor_goto()
    output.write('\n'.join(format_text()) + '\n')
    output.flush()
    output.cursor_goto()
    output.erase_down()


def control_loop():
    output.hide_cursor()
    while True:
        keys = input_.read_keys()
        if keys:
            for key in keys:
                on_key(key)
        redraw()
        time.sleep(.01)


control_loop()
