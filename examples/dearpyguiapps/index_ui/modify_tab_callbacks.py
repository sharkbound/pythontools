from dearpygui.dearpygui import get_value, set_value

from constants import ModifyID
from sqllib import Tag, query, Record, commit, load_tags_from_id_database


def set_error(msg):
    set_value(ModifyID.ERROR_TEXT, msg)


def validate_record_id(record_id):
    if not Record.exists_by_id(record_id):
        set_error(f'invalid record id: {record_id}')
        return False
    return True


def load_tags_from_input():
    return [tag.strip().lower() for tag in get_value(ModifyID.TAGS_INPUT).split(',')]


def _update_record_fields(record):
    if record is not None:
        record_id, location, summary = record.id, record.location, record.summary
    else:
        record_id = 0
        location = summary = ''

    if record_id:
        set_value(ModifyID.ID_INPUT, record_id)
        set_value(ModifyID.TAGS_INPUT, ', '.join(load_tags_from_id_database(record_id)))
        set_error('')
    set_value(ModifyID.LOCATION_INPUT, location)
    set_value(ModifyID.SUMMARY_INPUT, summary)


def cb_load_from_id(sender, data):
    id = get_value(ModifyID.ID_INPUT)

    if not validate_record_id(id):
        return

    record = query(Record).filter(Record.id == id).one_or_none()
    _update_record_fields(record)


def cb_set_tags(sender, data):
    record_id = get_value(ModifyID.ID_INPUT)
    if not validate_record_id(record_id):
        return

    query(Tag).filter(Tag.record_id == record_id).delete()
    for tag in load_tags_from_input():
        Tag.new(tag, record_id)

    set_error('')


def cb_add_record(sender, data):
    summary = get_value(ModifyID.SUMMARY_INPUT).strip()
    if not summary:
        set_error('no summary is set!')
        return

    if Record.exists_by_summary_exact(summary):
        set_error('duplicate record summary')
        return

    record = Record.new(summary, get_value(ModifyID.LOCATION_INPUT).lower().strip())
    set_value(ModifyID.ID_INPUT, record.id)

    tags = load_tags_from_input()
    for tag in tags:
        Tag.new(tag, record.id)

    set_error('')
    set_value(ModifyID.ID_INPUT, 0)
    set_value(ModifyID.TAGS_INPUT, '')
    set_value(ModifyID.LOCATION_INPUT, '')
    set_value(ModifyID.SUMMARY_INPUT, '')


def cb_set_summary(sender, data):
    record_id = get_value(ModifyID.ID_INPUT)
    if not validate_record_id(record_id):
        return

    record = query(Record).filter(Record.id == record_id).one_or_none()
    if record is None:
        set_error(f'could not find record by id: {record_id}')
        return

    summary = get_value(ModifyID.SUMMARY_INPUT).strip()
    if not summary:
        set_error('summary must not be empty!')
        return

    record.summary = summary
    commit()
    set_error('')


def cb_set_location(sender, data):
    record_id = get_value(ModifyID.ID_INPUT)
    if not validate_record_id(record_id):
        return

    record = query(Record).filter(Record.id == record_id).one_or_none()
    if record is None:
        set_error(f'could not find record by id: {record_id}')
        return

    record.location = get_value(ModifyID.LOCATION_INPUT).lower().strip()
    commit()
    set_error('')
