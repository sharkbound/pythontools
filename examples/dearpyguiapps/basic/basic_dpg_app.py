import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

import traceback

traceback.print_exc()


class IDStore:
    def __getattr__(self, item):
        return item


ID = IDStore()

show_demo()

with dpg.value_registry():
    dpg.add_series_value(tag='src')


def cb_add_3d_coords():
    with dpg.table_row(parent=ID.table1):
        for n in dpg.get_value(ID.values3):
            dpg.add_text(label=str(n))


with dpg.theme(tag='__round'):
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 30, 30)

with dpg.window(label='basic dpg app', tag='main'):
    with dpg.group(horizontal=False):
        dpg.add_3d_slider(tag=ID.values3, scale=.3, callback=lambda: print(dpg.get_value(ID.values3)))
        dpg.add_button(label='add coords', callback=cb_add_3d_coords)
        dpg.bind_item_theme(dpg.last_item(), '__round')

    with dpg.table(tag=ID.table1, source='src'):
        dpg.add_table_column(label='x')
        dpg.add_table_column(label='y')
        dpg.add_table_column(label='z')

dpg.set_primary_window('main', True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
