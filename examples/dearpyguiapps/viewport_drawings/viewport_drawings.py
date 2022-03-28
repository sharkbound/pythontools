import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(tag='main', no_background=True):
    with dpg.viewport_drawlist(tag='layer1', front=False):
        dpg.draw_rectangle([200, 200], [400, 400], fill=[255, 0, 0])
    dpg.add_input_text(label='text', pos=[300, 300], width=100)

dpg.set_primary_window('main', True)
dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
