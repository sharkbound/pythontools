import dearpygui.dearpygui as dpg
from .ids import AllIds


def callback_extract_audio_select_video():
    dpg.show_item(AllIds.FILE_DIALOG_EXTRACT_AUDIO_VIDEO_PATH)
