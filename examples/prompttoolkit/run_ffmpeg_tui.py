#
# os.system('start cmd /C "conda activate py310tui && python -m file_selector_ui"')


import os
import sys
from pathlib import Path
import questionary
from file_selector_ui import FileSelector

ROOT_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else '.')


def is_valid_output_filename(filename):
    return all(c for c in filename if c.strip() and c.isascii())


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return 'input must be a valid float (ex: 2.0, 2.5, 3)'


def is_int(value):
    try:
        float(value)
        return True
    except ValueError:
        return 'input must be a valid int (ex: 2, 3, 10)'


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
    VALID_EXTENSIONS = ['.mp3', '.mp4', '.webm']

    path = launch_file_selector(initial_path=ROOT_DIR, selection_validator=lambda p: p.suffix.lower() in VALID_EXTENSIONS)
    volume = questionary.text('Enter amount to boost volume by: ', validate=is_float).ask()
    outfile = CWD / (questionary.text('Enter output file name: ', validate=is_valid_output_filename).ask() + path.suffix)
    args = ['ffmpeg', '-i', f'"{path}"', '-filter:a', f'"volume={volume}" "{outfile}"']

    execute_console_command_and_check_output(args, outfile)


def handle_mode_extract_audio():
    VALID_EXTENSIONS = ['.mp4', '.mkv']

    path = launch_file_selector(initial_path=ROOT_DIR, selection_validator=lambda p: p.suffix.lower() in VALID_EXTENSIONS)
    outfile = CWD / (questionary.text('Enter output file name: ', validate=is_valid_output_filename).ask() + '.mp3')
    args = ['ffmpeg', f'-i "{path}"', '-q:a 0', '-map a', f'"{outfile}"']

    execute_console_command_and_check_output(args, outfile)


mode = questionary.select('select an FFMPEG operation:', FFMPEGMode.ALL, use_shortcuts=True).ask()


def ask_hour_minute_second(mode):
    def _is_int_or_empty(value):
        if value:
            return is_int(value)
        return True

    if mode == 'start':
        ask = lambda type: questionary.text(f'enter the {type.upper()} as an two digit number (default 0): ', validate=_is_int_or_empty).ask().zfill(
            2)
        return {'hour': ask('hour'), 'minute': ask('minute'), 'second': ask('second')}
    elif mode == 'duration':
        ask = lambda type: questionary.text(f'enter duration of {type.upper()}s to include in the audio slice (default 0): ',
                                            validate=_is_int_or_empty).ask().zfill(2)
        return {'hour': ask('hour'), 'minute': ask('minute'), 'second': ask('second')}


def handle_mode_slice_audio():
    VALID_EXTENSIONS = ['.mp3']
    path = launch_file_selector(initial_path=ROOT_DIR, selection_validator=lambda p: p.suffix.lower() in VALID_EXTENSIONS)
    hms_start = ask_hour_minute_second('start')
    hms_duration = ask_hour_minute_second('duration')
    outfile = CWD / (questionary.text('Enter output file name: ', validate=is_valid_output_filename).ask() + '.mp3')

    args = [
        'ffmpeg',
        f'-i "{path}"',
        '-ss', ':'.join((hms_start['hour'], hms_start['minute'], hms_start['second'])),
        '-t', ':'.join((hms_duration['hour'], hms_duration['minute'], hms_duration['second'])),
        f'"{outfile}"'
    ]
    execute_console_command_and_check_output(args, outfile)


if mode == FFMPEGMode.INCREASE_VOLUME:
    handle_mode_increase_volume()
elif mode == FFMPEGMode.EXTRACT_AUDIO:
    handle_mode_extract_audio()
elif mode == FFMPEGMode.SLICE_AUDIO:
    handle_mode_slice_audio()
