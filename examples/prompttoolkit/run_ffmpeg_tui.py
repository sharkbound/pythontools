#
# os.system('start cmd /C "conda activate py310tui && python -m file_selector_ui"')


import os
from pathlib import Path

import questionary
from subprocess import check_output, PIPE
from file_selector_ui import FileSelector


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return 'input must be a valid float (ex: 2.0, 2.5, 3)'


class FFMPEGMode:
    INCREASE_VOLUME = 'increase volume'
    EXTRACT_AUDIO = 'extract audio'
    SLICE_AUDIO = 'slice audio'
    ALL = [INCREASE_VOLUME, EXTRACT_AUDIO, SLICE_AUDIO]


CWD = Path.cwd()


def handle_mode_increase_volume():
    VALID_EXTENSIONS = ['.mp3']

    if (path := FileSelector(lambda p: p.suffix.lower() in VALID_EXTENSIONS).start()) is None:
        input('Selecting a PATH is required.')
        exit(1)

    volume = questionary.text('Enter amount to boost volume by: ', validate=is_float).ask()
    outfile = CWD / (questionary.text('Enter output file name: ', validate=lambda x: x.isalnum()).ask() + path.suffix)
    args = ['ffmpeg', '-i', f'"{path}"', '-filter:a', f'"volume={volume}" "{outfile}"']

    if (exit_code := os.system(' '.join(args))) == 0:
        print('\n\n=====================================')
        print(f'DONE! Outputted result to path: \n\n\t{outfile}')
        print('=====================================')


def handle_mode_extract_audio():
    VALID_EXTENSIONS = ['.mp4']

    if (path := FileSelector(lambda p: p.suffix.lower() in VALID_EXTENSIONS).start()) is None:
        print('Selecting a PATH is required.')
        exit(1)

    outfile = CWD / (questionary.text('Enter output file name: ', validate=lambda x: x.isalnum()).ask() + '.mp3')
    args = ['ffmpeg', f'-i "{path}"', '-q:a 0', '-map a', f'"{outfile}"']

    if (exit_code := os.system(' '.join(args))) == 0:
        print('\n\n=====================================')
        print(f'DONE! Outputted result to path: \n\n\t{outfile}')
        print('=====================================')


mode = questionary.select('select an FFMPEG operation:', FFMPEGMode.ALL, use_shortcuts=True).ask()

if mode == FFMPEGMode.INCREASE_VOLUME:
    handle_mode_increase_volume()
elif mode == FFMPEGMode.EXTRACT_AUDIO:
    handle_mode_extract_audio()
