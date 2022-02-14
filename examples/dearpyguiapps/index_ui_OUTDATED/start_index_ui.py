from dearpygui.dearpygui import *
from constants import FindID, ModifyID

import find_tab_callbacks
import modify_tab_callbacks


def add_ui_items():
    with window(label='IndexUI', tag='IndexUI'):
        with tab_bar(label='alltabs'):
            with tab(label='modify'):
                add_input_text(label=ModifyID.SUMMARY_INPUT, tag=ModifyID.SUMMARY_INPUT)
                add_button(label=ModifyID.SUMMARY_INPUT_SET_BUTTON, tag=ModifyID.SUMMARY_INPUT_SET_BUTTON,
                           callback=modify_tab_callbacks.cb_set_summary)

                add_input_text(label=ModifyID.TAGS_INPUT, tag=ModifyID.TAGS_INPUT)
                add_button(label=ModifyID.TAGS_INPUT_SET_BUTTON, tag=ModifyID.TAGS_INPUT_SET_BUTTON, callback=modify_tab_callbacks.cb_set_tags)

                add_input_int(label=ModifyID.ID_INPUT, tag=ModifyID.ID_INPUT)
                add_button(label=ModifyID.LOAD_FROM_ID_BUTTON, tag=ModifyID.LOAD_FROM_ID_BUTTON, callback=modify_tab_callbacks.cb_load_from_id)

                add_input_text(label=ModifyID.LOCATION_INPUT, tag=ModifyID.LOCATION_INPUT)
                add_button(label=ModifyID.LOCATION_INPUT_SET_BUTTON, tag=ModifyID.LOCATION_INPUT_SET_BUTTON,
                           callback=modify_tab_callbacks.cb_set_location)

                add_button(label=ModifyID.ADD_RECORD_BUTTON, tag=ModifyID.ADD_RECORD_BUTTON, callback=modify_tab_callbacks.cb_add_record)
                add_input_text(label=ModifyID.ERROR_TEXT, tag=ModifyID.ERROR_TEXT, readonly=True)

            with tab(label='find', tag='find'):
                with group(horizontal=True):
                    add_input_int(label=FindID.RECORD_ID, tag=FindID.RECORD_ID, callback=find_tab_callbacks.cb_find_by_id, on_enter=True)
                    add_button(label=FindID.FIND_BY_ID, tag=FindID.FIND_BY_ID, callback=find_tab_callbacks.cb_find_by_id)

                with group(horizontal=True):
                    add_input_text(label=FindID.SUMMARY, tag=FindID.SUMMARY, callback=find_tab_callbacks.cb_find_by_summary, on_enter=True)
                    add_button(label=FindID.FIND_BY_SUMMARY, tag=FindID.FIND_BY_SUMMARY, callback=find_tab_callbacks.cb_find_by_summary)

                with group(horizontal=True):
                    add_input_text(label=FindID.TAGS, tag=FindID.TAGS, callback=find_tab_callbacks.cb_find_by_tags, on_enter=True)
                    add_button(label=FindID.FIND_BY_TAG, tag=FindID.FIND_BY_TAG, callback=find_tab_callbacks.cb_find_by_tags)

                add_input_text(label=FindID.READ_ONLY_LOCATION, tag=FindID.READ_ONLY_LOCATION, readonly=True)

                with table(label=FindID.RESULT_TABLE, tag=FindID.RESULT_TABLE):
                    for column_name in ('id', 'tags', 'location', 'summary'):
                        add_table_column(label=column_name)


def main():
    if __name__ == '__main__':
        create_context()
        create_viewport()
        setup_dearpygui()

        add_ui_items()
        set_primary_window('IndexUI', True)

        show_viewport()
        start_dearpygui()
        destroy_context()


main()
