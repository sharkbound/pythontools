import dearpygui.dearpygui as dpg
from . import callbacks
from .ids import AllIds

INITIAL_VIEWPORT_SIZE = 800, 600


def _init_file_dialogs():
    with dpg.file_dialog(
            label=AllIds.FILE_DIALOG_EXTRACT_AUDIO_VIDEO_PATH,
            tag=AllIds.FILE_DIALOG_EXTRACT_AUDIO_VIDEO_PATH,
            show=False,
            # callback=lambda x: print(x)
    ):
        dpg.add_file_extension('*.mp4')


def start():
    _init_dpg()
    _init_file_dialogs()
    _init_dpg_elements()
    _show_dpg()


def _init_dpg_elements():
    with dpg.window(label=AllIds.WINDOW_EXTRACT_AUDIO, tag=AllIds.WINDOW_EXTRACT_AUDIO, width=400):
        # with dpg.group(horizontal=True):
        dpg.add_input_text(label=AllIds.INPUT_EXTRACT_AUDIO_FILE_PATH, tag=AllIds.INPUT_EXTRACT_AUDIO_FILE_PATH)
        dpg.add_button(label=AllIds.BUTTON_EXTRACT_AUDIO_SELECT_VIDEO, tag=AllIds.BUTTON_EXTRACT_AUDIO_SELECT_VIDEO,
                       before=AllIds.INPUT_EXTRACT_AUDIO_FILE_PATH, callback=callbacks.callback_extract_audio_select_video)
        dpg.add_button(label=AllIds.BUTTON_EXTRACT_AUDIO_EXTRACT_AUDIO, tag=AllIds.BUTTON_EXTRACT_AUDIO_EXTRACT_AUDIO)


def _show_dpg():
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def _init_dpg():
    dpg.create_context()
    dpg.create_viewport(width=INITIAL_VIEWPORT_SIZE[0], height=INITIAL_VIEWPORT_SIZE[1])
    dpg.setup_dearpygui()
