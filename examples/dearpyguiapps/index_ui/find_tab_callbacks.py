from collections import defaultdict
from threading import current_thread

from dearpygui.dearpygui import set_value, get_value, get_item_children, delete_item, table_row, add_button, get_item_configuration
from icecream import ic
from sqlalchemy import or_

from constants import FindID
from sqllib import *


def clear_table(table_tag):
    for tag in get_item_children(table_tag)[1]:
        delete_item(tag)


def set_table_data(tag, data):
    clear_table(tag)
    for i, record in enumerate(data):
        with table_row(parent=tag, tag=f'row_{i}'):
            add_button(label=record[0], callback=lambda: cb_table_result_selected(f'row_{i}'))
            add_button(label=', '.join(load_tags_from_id_database(record[0])), callback=lambda: cb_table_result_selected(f'row_{i}'))
            add_button(label=record[2], callback=lambda: cb_table_result_selected(f'row_{i}'))
            add_button(label=record[3], callback=lambda: cb_table_result_selected(f'row_{i}'))
        # [
        #     record.id,
        #     ', '.join(load_tags_from_id_database(record.id)),
        #     record.location,
        #     record.summary
        # ]
        # for record in records


def _set_readonly_fields(id, summary, tags, location):
    set_value(FindID.RECORD_ID, id)
    set_value(FindID.SUMMARY, summary)
    set_value(FindID.TAGS, tags)
    set_value(FindID.READ_ONLY_LOCATION, location)


def _load_record_from_id(record_id):
    record = query(Record).filter(Record.id == record_id).one_or_none()
    if record is None:
        _set_readonly_fields(get_value(FindID.RECORD_ID), '', '', '')
        return
    _set_readonly_fields(record.id, record.summary, ', '.join(load_tags_from_id_database(record.id)), record.location)


def cb_find_by_id(sender, data):
    clear_table(FindID.RESULT_TABLE)
    _load_record_from_id(get_value(FindID.RECORD_ID))


def cb_find_by_summary(sender, data):
    clear_table(FindID.RESULT_TABLE)
    summary = get_value(FindID.SUMMARY).strip()
    if not summary:
        return

    records = query(Record).filter(Record.summary.contains(summary)).all()
    data = [[record.id, ', '.join(load_tags_from_id_database(record.id)), record.location, record.summary] for record in records]
    set_table_data(FindID.RESULT_TABLE, data)


def cb_find_by_tags():
    if not (user_tags := [tag_stripped for tag in get_value(FindID.TAGS).strip().split(',') if (tag_stripped := tag.strip())]):
        return

    grouped_tags = defaultdict(list)
    for tag in query(Tag).filter(or_(*(Tag.name == tag.lower() for tag in user_tags))).all():
        grouped_tags[tag.record_id].append(tag)

    for record_id in list(grouped_tags):
        names = {tag.name for tag in grouped_tags[record_id]}
        if not all(tag in names for tag in user_tags):
            del grouped_tags[record_id]

    set_table_data(FindID.RESULT_TABLE,
                   [
                       [
                           record.id,
                           ', '.join(load_tags_from_id_database(record.id)),
                           record.location,
                           record.summary
                       ]
                       for record in query(Record).filter(or_(*(Record.id == id for id in grouped_tags)))
                   ])


def _try_parse_int(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default


def cb_table_result_selected(row_tag):
    children = get_item_children(row_tag)
    child_value = get_item_configuration(children[1][0])['label']
    _load_record_from_id(_try_parse_int(child_value))
