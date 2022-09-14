import collections
from time import time

import dearpygui.dearpygui as dpg

from config import Config

WIDTH = 350
HEIGHT = 300

FormattedSeconds = collections.namedtuple('FormattedSeconds', 'total_seconds hours minutes seconds')


def format_seconds(seconds):
    remaining_seconds = int(seconds)
    hours = remaining_seconds // 3600
    remaining_seconds -= hours * 3600
    minutes = remaining_seconds // 60
    remaining_seconds -= minutes * 60

    return FormattedSeconds(
        total_seconds=seconds,
        hours=hours,
        minutes=minutes,
        seconds=remaining_seconds
    )


cfg = Config('records.json', start=0, end=0, paused=False, pauses=[], previous=[])


def setup_gui():
    with dpg.theme(tag='__round'):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 30, 30)

    with dpg.font_registry():
        dpg.add_font('C:/Windows/Fonts/impact.ttf', size=50, tag='big_impact')
        dpg.add_font('C:/Windows/Fonts/impact.ttf', size=25, tag='lesser_impact')

    with dpg.window(tag='main'):
        add_timer_control_elements()
        add_elapsed_time_elements()
        add_pause_control_elements()


def add_timer_control_elements():
    with dpg.group(horizontal=True):
        dpg.add_button(label='Start Time', callback=start_time_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='End Time', callback=end_time_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')


def add_pause_control_elements():
    with dpg.group(horizontal=True):
        dpg.add_button(label='Start Pause', callback=start_paused_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='End Pause', callback=end_paused_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')


def add_elapsed_time_elements():
    with dpg.group(horizontal=True):
        dpg.add_text('ELAPSED TIME:')
        dpg.bind_item_font(dpg.last_item(), 'lesser_impact')
        dpg.add_text('00:00:00', tag='_elapsed_time_label')
        dpg.bind_item_font(dpg.last_item(), 'big_impact')


def update_elapsed_time_labels():
    if not cfg.start:
        return

    formatted_diff = format_seconds(abs(cfg.start - (cfg.end or time())))
    print(f'{formatted_diff.hours:0>2}:{formatted_diff.minutes:0>2}:{formatted_diff.seconds:0>2}')
    dpg.set_item_label('_elapsed_time_label', f'{formatted_diff.hours:0>2}:{formatted_diff.minutes:0>2}:{formatted_diff.seconds:0>2}')


def start_time_clicked(sender, _, data):
    print('yes')
    cfg.start = int(time())


def end_time_clicked(sender, _, data):
    cfg.end = int(time())


def start_paused_clicked(sender, _, data):
    pass


def end_paused_clicked(sender, _, data):
    pass


def run():
    dpg.create_context()
    dpg.create_viewport(width=WIDTH, height=HEIGHT, title='Hourly Time Calculator')
    dpg.setup_dearpygui()

    setup_gui()

    dpg.set_primary_window('main', True)
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        update_elapsed_time_labels()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


if __name__ == '__main__':
    run()
