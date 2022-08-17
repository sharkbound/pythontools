#
# os.system('start cmd /C "conda activate py310tui && python -m file_selector_ui"')


import os
import sys
from pathlib import Path
import questionary
from file_selector_ui import FileSelector

ROOT_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else '.')


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
    ALL = (INCREASE_VOLUME, EXTRACT_AUDIO, SLICE_AUDIO)


CWD = Path.cwd()


def launch_file_selector(initial_path, selection_validator):
    if (path := FileSelector(selection_validator=selection_validator, initial_path=initial_path).start()) is None:
        input('Selecting a PATH is required.')
        exit(1)
    return path


def execute_console_command_and_check_output(args, outfile):
    if (exit_code := os.system(' '.join(args))) == 0:
        print('\n\n=====================================')
        print(f'DONE! Outputted result to path: \n\n\t{outfile}')
        print('=====================================')


def handle_mode_increase_volume():
    VALID_EXTENSIONS = ['.mp3']

    path = launch_file_selector(initial_path=ROOT_DIR, selection_validator=lambda p: p.suffix.lower() in VALID_EXTENSIONS)
    volume = questionary.text('Enter amount to boost volume by: ', validate=is_float).ask()
    outfile = CWD / (questionary.text('Enter output file name: ', validate=lambda x: x.isalnum()).ask() + path.suffix)
    args = ['ffmpeg', '-i', f'"{path}"', '-filter:a', f'"volume={volume}" "{outfile}"']

    execute_console_command_and_check_output(args, outfile)


def handle_mode_extract_audio():
    VALID_EXTENSIONS = ['.mp4']

    path = launch_file_selector(initial_path=ROOT_DIR, selection_validator=lambda p: p.suffix.lower() in VALID_EXTENSIONS)
    outfile = CWD / (questionary.text('Enter output file name: ', validate=lambda x: x.isalnum()).ask() + '.mp3')
    args = ['ffmpeg', f'-i "{path}"', '-q:a 0', '-map a', f'"{outfile}"']

    execute_console_command_and_check_output(args, outfile)


mode = questionary.select('select an FFMPEG operation:', FFMPEGMode.ALL, use_shortcuts=True).ask()


def handle_mode_slice_audio():
    VALID_EXTENSIONS = ['.mp3']
    # todo: make this use -ss -t for ffmpeg arguments
    path = launch_file_selector(initial_path=ROOT_DIR, selection_validator=lambda p: p.suffix.lower() in VALID_EXTENSIONS)
    outfile = CWD / (questionary.text('Enter output file name: ', validate=lambda x: x.isalnum()).ask() + '.mp3')
    args = ['ffmpeg', f'-i "{path}"', '-q:a 0', '-map a', f'"{outfile}"']

    execute_console_command_and_check_output(args, outfile)


if mode == FFMPEGMode.INCREASE_VOLUME:
    handle_mode_increase_volume()
elif mode == FFMPEGMode.EXTRACT_AUDIO:
    handle_mode_extract_audio()
elif mode == FFMPEGMode.SLICE_AUDIO:
    handle_mode_slice_audio()
