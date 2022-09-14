import collections
from datetime import datetime
from time import time

import dearpygui.dearpygui as dpg
import pyperclip

from config import Config

WIDTH = 550
HEIGHT = 400

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


cfg = Config('records.json', start=0, end=0, start_pause=0, end_pause=0, paused=False, pauses=[])


def setup_gui():
    with dpg.theme(tag='__round'):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)

    with dpg.font_registry():
        dpg.add_font('C:/Windows/Fonts/impact.ttf', size=100, tag='big_impact')
        dpg.add_font('C:/Windows/Fonts/impact.ttf', size=25, tag='lesser_impact')

    with dpg.window(tag='main'):
        add_timer_control_elements()
        add_elapsed_time_elements()
        add_hourly_pay_elements()


def add_timer_control_elements():
    with dpg.group(horizontal=True):
        dpg.add_button(label='Start Time', callback=start_time_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='End Time', callback=end_time_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='Start Pause', callback=start_paused_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='End Pause', callback=end_paused_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')

    with dpg.group(horizontal=True):
        dpg.add_button(label='Reset', callback=reset_start_end_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='Clear End', callback=clear_end_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')
        dpg.add_button(label='Clear Pauses', callback=clear_pauses_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')


def clear_end_clicked(sender, _, data):
    cfg['end'] = 0
    cfg.save()


def clear_pauses_clicked(sender, _, data):
    cfg['pauses'] = []
    cfg['start_pause'] = 0
    cfg['end_pause'] = 0
    cfg.save()


def copy_epoch_time_stamp_in_human_readable_format_clicked(sender, _, data):
    if data == 'start' and cfg.start != 0:
        pyperclip.copy(format_epoch_time(cfg.start))
    elif data == 'end' and cfg.end != 0:
        pyperclip.copy(format_epoch_time(cfg.end))


def add_hourly_pay_elements():
    dpg.add_input_float(label='Pay-Per-Hour', tag='pay_per_hour', default_value=25)

    with dpg.group(horizontal=True):
        dpg.add_button(label='Copy Pay', callback=lambda _, __, ___: pyperclip.copy(str(round(calculate_pay(), 2))))
        dpg.bind_item_theme(dpg.last_item(), '__round')

        dpg.add_button(label='Copy Start UTC Time', user_data='start', callback=copy_epoch_time_stamp_in_human_readable_format_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')

        dpg.add_button(label='Copy End UTC Time', user_data='end', callback=copy_epoch_time_stamp_in_human_readable_format_clicked)
        dpg.bind_item_theme(dpg.last_item(), '__round')

    with dpg.group(horizontal=True):
        dpg.add_spacer(width=100)
        dpg.add_text('$0', tag='current_pay')
        dpg.bind_item_font(dpg.last_item(), 'big_impact')


def format_epoch_time(epoch_timestamp):
    return datetime.utcfromtimestamp(epoch_timestamp).strftime('%I:%M %p UTC')


def add_elapsed_time_elements():
    with dpg.group(horizontal=True):
        dpg.add_spacer(width=70)
        dpg.add_text('00:00:00', tag='elapsed_time_label')
        dpg.bind_item_font(dpg.last_item(), 'big_impact')


def update_labels():
    if not cfg.start:
        return

    formatted_diff = format_seconds(abs(cfg.start - (cfg.end or time())))
    dpg.set_value('elapsed_time_label', f'{formatted_diff.hours:0>2}:{formatted_diff.minutes:0>2}:{formatted_diff.seconds:0>2}')
    if cfg.start_pause == 0:
        update_pay()


def update_pay():
    if not cfg.start:
        return 0

    due_pay = calculate_pay()
    dpg.set_value('current_pay', f'${round(due_pay, 2)}')


def ensure_start_and_end(start, end=None):
    """
    replace None or 0 with the current epoch time
    """
    NOW = time()
    if end is None or end == 0:
        end = NOW
    if start is None or start == 0:
        start = NOW
    return start, end


def formatted_seconds_diff(start, end=None):
    start, end = ensure_start_and_end(start, end)
    return format_seconds(abs(start - end))


def calculate_total_pause_seconds():
    start, end = ensure_start_and_end(cfg.start_pause, cfg.end_pause)
    return abs(start - end) + sum(pause['diff_seconds'] for pause in cfg.pauses)


def calculate_pay():
    start, end = ensure_start_and_end(cfg.start, cfg.end)
    formatted_diff = formatted_seconds_diff(start, end)
    pay_per_hour = dpg.get_value('pay_per_hour')
    due_pay = (((
                        (formatted_diff.hours * 3600)
                        + (formatted_diff.minutes * 60)
                        + formatted_diff.seconds
                ) / 3600)
              ) * pay_per_hour

    due_pay -= (calculate_total_pause_seconds() / 3600) * pay_per_hour
    return due_pay


def reset_start_end_clicked():
    cfg['start'] = 0
    cfg['end'] = 0
    cfg['start_pause'] = 0
    cfg['end_pause'] = 0
    cfg['pauses'] = []
    cfg.save()


def start_time_clicked(sender, _, data):
    cfg['start'] = int(time())
    cfg.save()


def end_time_clicked(sender, _, data):
    cfg['end'] = int(time())
    cfg.save()


def start_paused_clicked(sender, _, data):
    cfg['start_pause'] = int(time())
    cfg.save()


def end_paused_clicked(sender, _, data):
    cfg['end_pause'] = int(time())
    cfg.pauses.append(create_pause_dict(cfg.start_pause, cfg.end_pause))
    cfg['start_pause'] = 0
    cfg['end_pause'] = 0
    cfg.save()


def create_pause_dict(start, end):
    return {'start': start, 'end': end, 'diff_seconds': abs(start - end)}


def run():
    dpg.create_context()
    dpg.create_viewport(width=WIDTH, height=HEIGHT, title='Hourly Time Calculator')
    dpg.setup_dearpygui()

    setup_gui()

    dpg.set_primary_window('main', True)
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        update_labels()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


if __name__ == '__main__':
    run()
