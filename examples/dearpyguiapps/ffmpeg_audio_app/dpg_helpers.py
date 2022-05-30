from contextlib import contextmanager

import dearpygui.dearpygui as dpg


class DotAccessDict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


@contextmanager
def modify_item_config(item_id):
    if not dpg.does_item_exist(item_id):
        raise RuntimeError(f'item_id {item_id} does not exists')

    item_config = DotAccessDict(dpg.get_item_configuration(item_id))
    yield item_config
    dpg.configure_item(item_id)
