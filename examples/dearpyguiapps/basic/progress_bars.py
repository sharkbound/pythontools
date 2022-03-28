import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(tag='main'):
    dpg.add_progress_bar(label='Progress Bar', tag='progress_bar')

dpg.set_primary_window('main', True)
dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.set_value('progress_bar', dpg.get_value('progress_bar') + .001)
    dpg.render_dearpygui_frame()

dpg.destroy_context()
